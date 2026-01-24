// dashboard.js - Updated for SimpleChart

class Dashboard {
  constructor() {
    this.memoryChart = null;
    this.cpuChart = null;
    this.initialize();
  }

  async initialize() {
    console.log('Dashboard initializing...');
    
    // Initialize charts
    if (typeof SimpleChart !== 'undefined') {
      this.memoryChart = new SimpleChart('memoryChart', {
        color: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.2)'
      });
      
      this.cpuChart = new SimpleChart('cpuChart', {
        color: '#f56565',
        backgroundColor: 'rgba(245, 101, 101, 0.2)'
      });
    } else {
      console.warn('SimpleChart not loaded, charts disabled');
    }
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Load initial data
    await this.loadData();
    
    // Start updates
    setInterval(() => this.updateCharts(), 5000);
    
    console.log('Dashboard initialized');
  }

  setupEventListeners() {
    // Time range buttons
    document.querySelectorAll('.time-range-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.time-range-btn').forEach(b => 
          b.classList.remove('active')
        );
        e.target.classList.add('active');
        this.updateCharts();
      });
    });
    
    // Action buttons
    document.getElementById('forceStabilization')?.addEventListener('click', async () => {
      if (confirm('Force system stabilization? This will discard inactive tabs.')) {
        await chrome.runtime.sendMessage({ action: 'TRIGGER_STABILIZATION' });
        alert('Stabilization initiated');
      }
    });
    
    document.getElementById('clearWarnings')?.addEventListener('click', async () => {
      if (confirm('Clear all warnings?')) {
        await chrome.runtime.sendMessage({ action: 'ACKNOWLEDGE_WARNING' });
        this.loadWarnings();
        alert('Warnings cleared');
      }
    });
    
    // Test buttons
    document.getElementById('testWarning')?.addEventListener('click', async () => {
      await chrome.runtime.sendMessage({ action: 'TEST_WARNING' });
      setTimeout(() => this.loadData(), 1000);
    });
    
    document.getElementById('clearData')?.addEventListener('click', async () => {
      if (confirm('Clear all data?')) {
        await chrome.runtime.sendMessage({ action: 'CLEAR_DATA' });
        setTimeout(() => this.loadData(), 1000);
      }
    });
  }

  async loadData() {
    try {
      // Get metrics from background
      const response = await chrome.runtime.sendMessage({ action: 'GET_METRICS' });
      if (response?.metrics) {
        this.updateCharts(response.metrics);
      }
      
      // Get status
      const status = await chrome.runtime.sendMessage({ action: 'GET_STATUS' });
      if (status) {
        this.updateStatus(status);
      }
      
      // Load warnings
      this.loadWarnings();
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    }
  }

  updateCharts(metrics = []) {
    if (!this.memoryChart || !this.cpuChart || metrics.length === 0) {
      // Use sample data for testing
      const sampleData = Array.from({length: 20}, (_, i) => 
        30 + Math.sin(Date.now() / 1000 + i * 0.3) * 20 + Math.random() * 15
      );
      
      if (this.memoryChart) {
        this.memoryChart.setData(sampleData);
      }
      if (this.cpuChart) {
        this.cpuChart.setData(sampleData.map(v => v * 0.7 + Math.random() * 10));
      }
      return;
    }
    
    // Extract real data
    const memoryData = metrics.map(m => m.memory?.usage || 0);
    const cpuData = metrics.map(m => m.cpu?.usage || 0);
    
    if (this.memoryChart && memoryData.length > 0) {
      this.memoryChart.setData(memoryData);
    }
    
    if (this.cpuChart && cpuData.length > 0) {
      this.cpuChart.setData(cpuData);
    }
  }

  updateStatus(status) {
    const modeElement = document.getElementById('dashboardMode');
    if (modeElement) {
      modeElement.textContent = status.mode.replace('_', ' ').toUpperCase();
      modeElement.className = `mode-${status.mode.split('_')[0]}`;
    }
    
    // Update status indicators
    document.querySelectorAll('.status-value').forEach(el => {
      const type = el.dataset.type;
      if (type === 'metrics') {
        el.textContent = status.metricsCount || 0;
      }
    });
  }

  async loadWarnings() {
    try {
      const result = await chrome.storage.local.get(['currentWarning', 'metrics']);
      const warningsList = document.getElementById('warningsList');
      
      if (!warningsList) return;
      
      if (!result.currentWarning) {
        warningsList.innerHTML = `
          <div class="no-warnings">
            <div class="no-warnings-icon">✅</div>
            <p>No active warnings</p>
            <p class="text-light">System is operating normally</p>
          </div>
        `;
        return;
      }
      
      const warning = result.currentWarning;
      const html = `
        <div class="warning-item ${warning.overallConfidence > 0.8 ? 'critical' : ''}">
          <div class="warning-header">
            <div class="warning-metric">
              <span class="status-indicator ${warning.overallConfidence > 0.8 ? 'status-indicator-critical' : 'status-indicator-warning'}"></span>
              <span>Regime Shift Detected</span>
            </div>
            <div class="warning-time">${new Date(warning.timestamp).toLocaleTimeString()}</div>
          </div>
          <div class="warning-details">
            ${warning.shifts.map(shift => `
              <div class="shift-item">
                <strong>${shift.metric}:</strong> 
                <span class="confidence-${shift.severity}">
                  ${(shift.probability * 100).toFixed(1)}% confidence
                </span>
                (${shift.severity})
              </div>
            `).join('')}
          </div>
        </div>
      `;
      
      warningsList.innerHTML = html;
      
    } catch (error) {
      console.error('Error loading warnings:', error);
    }
  }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.dashboard = new Dashboard();
});