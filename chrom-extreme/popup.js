// Popup script for RegimeShift Sentinel

class PopupController {
  constructor() {
    this.initialize();
  }

  async initialize() {
    // Load current metrics and status
    await this.loadMetrics();
    await this.loadStatus();
    await this.checkForWarnings();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Start periodic updates
    setInterval(() => this.loadMetrics(), 2000);
    setInterval(() => this.loadStatus(), 5000);
  }

  async loadMetrics() {
    try {
      const result = await chrome.storage.local.get(['currentMetrics']);
      
      if (result.currentMetrics) {
        this.updateMetricsDisplay(result.currentMetrics);
      }
    } catch (error) {
      console.error('Error loading metrics:', error);
    }
  }

  async loadStatus() {
    try {
      const response = await chrome.runtime.sendMessage({ action: 'GET_STATUS' });
      
      if (response) {
        this.updateStatusDisplay(response);
      }
    } catch (error) {
      console.error('Error loading status:', error);
    }
  }

  async checkForWarnings() {
    try {
      const result = await chrome.storage.local.get(['currentWarning']);
      
      if (result.currentWarning) {
        this.showWarning(result.currentWarning);
      } else {
        this.hideWarning();
      }
    } catch (error) {
      console.error('Error checking warnings:', error);
    }
  }

  updateMetricsDisplay(metrics) {
    // Update system health
    const health = 100 - Math.max(metrics.memory.usage, metrics.cpu.usage);
    document.getElementById('systemHealth').textContent = `${health.toFixed(0)}%`;
    
    // Update memory
    document.getElementById('memoryUsage').textContent = `${metrics.memory.usage.toFixed(1)}%`;
    document.getElementById('memoryProgress').value = metrics.memory.usage;
    
    // Update CPU
    document.getElementById('cpuLoad').textContent = `${metrics.cpu.usage.toFixed(1)}%`;
    document.getElementById('cpuProgress').value = metrics.cpu.usage;
    
    // Update trend indicator
    const trendElement = document.getElementById('systemTrend');
    const trend = this.calculateTrend(metrics);
    trendElement.textContent = trend;
    trendElement.className = `metric-trend trend-${trend}`;
  }

  calculateTrend(metrics) {
    // Simplified trend calculation
    if (metrics.memory.usage > 80 || metrics.cpu.usage > 80) {
      return '↑ Rising';
    } else if (metrics.memory.usage < 30 && metrics.cpu.usage < 30) {
      return '↓ Falling';
    }
    return '→ Stable';
  }

  updateStatusDisplay(status) {
    const modeElement = document.getElementById('currentMode');
    const statusIndicator = document.getElementById('statusIndicator');
    
    // Update mode display
    const modeNames = {
      'adaptive_observation': 'Adaptive Observation',
      'warning': 'Warning Mode',
      'stabilization': 'Stabilization Mode'
    };
    
    modeElement.textContent = modeNames[status.mode] || status.mode;
    
    // Update status indicator color
    if (status.mode === 'warning') {
      statusIndicator.style.background = '#FFC107';
      statusIndicator.style.animation = 'pulse 0.5s infinite';
    } else if (status.mode === 'stabilization') {
      statusIndicator.style.background = '#4CAF50';
      statusIndicator.style.animation = 'none';
    } else {
      statusIndicator.style.background = '#2196F3';
      statusIndicator.style.animation = 'pulse 2s infinite';
    }
  }

  showWarning(warning) {
    const panel = document.getElementById('warningPanel');
    const details = document.getElementById('warningDetails');
    const confidence = document.getElementById('confidenceLevel');
    
    panel.style.display = 'block';
    
    // Build warning details
    const shiftDetails = warning.shifts.map(shift => 
      `${shift.metric}: ${(shift.probability * 100).toFixed(1)}% confidence (${shift.severity})`
    ).join('<br>');
    
    details.innerHTML = `Multiple regime shifts detected:<br>${shiftDetails}`;
    confidence.textContent = `${(warning.overallConfidence * 100).toFixed(1)}%`;
    
    // Update confidence color
    if (warning.overallConfidence > 0.8) {
      confidence.style.color = '#ff4444';
    } else if (warning.overallConfidence > 0.6) {
      confidence.style.color = '#ffbb33';
    } else {
      confidence.style.color = '#00C851';
    }
  }

  hideWarning() {
    document.getElementById('warningPanel').style.display = 'none';
  }

  setupEventListeners() {
    // Stabilize button
    document.getElementById('stabilizeBtn').addEventListener('click', async () => {
      await chrome.runtime.sendMessage({ action: 'TRIGGER_STABILIZATION' });
      this.hideWarning();
    });
    
    // Ignore button
    document.getElementById('ignoreBtn').addEventListener('click', async () => {
      await chrome.runtime.sendMessage({ action: 'ACKNOWLEDGE_WARNING' });
      this.hideWarning();
    });
    
    // Details button
    document.getElementById('detailsBtn').addEventListener('click', () => {
      chrome.tabs.create({ url: chrome.runtime.getURL('dashboard.html') });
    });
    
    // Open Dashboard button
    document.getElementById('openDashboard').addEventListener('click', () => {
      chrome.tabs.create({ url: chrome.runtime.getURL('dashboard.html') });
    });
    
    // Settings button
    document.getElementById('settingsBtn').addEventListener('click', () => {
      this.showSettings();
    });
  }

  async showSettings() {
    // Load current settings
    const settings = await chrome.runtime.sendMessage({ action: 'GET_SETTINGS' });
    
    // Create settings modal
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-content">
        <h2>Settings</h2>
        <div class="form-group">
          <label>Confidence Threshold</label>
          <input type="range" id="confidenceThreshold" min="0.5" max="0.95" step="0.05" value="${settings.confidenceThreshold || 0.75}">
          <span id="thresholdValue">${(settings.confidenceThreshold || 0.75) * 100}%</span>
        </div>
        <div class="form-group">
          <label>Window Size (data points)</label>
          <input type="number" id="windowSize" min="10" max="200" value="${settings.windowSize || 50}">
        </div>
        <div class="form-group">
          <label>
            <input type="checkbox" id="monitoringEnabled" ${settings.monitoringEnabled !== false ? 'checked' : ''}>
            Enable Monitoring
          </label>
        </div>
        <div class="modal-buttons">
          <button id="saveSettings" class="btn btn-primary">Save</button>
          <button id="closeModal" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add modal styles
    const style = document.createElement('style');
    style.textContent = `
      .modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
      }
      .modal-content {
        background: white;
        padding: 20px;
        border-radius: 8px;
        width: 300px;
        color: #333;
      }
      .form-group {
        margin: 15px 0;
      }
      .form-group label {
        display: block;
        margin-bottom: 5px;
        font-weight: 600;
      }
      .form-group input[type="range"] {
        width: 70%;
      }
      #thresholdValue {
        margin-left: 10px;
        font-weight: bold;
      }
      .modal-buttons {
        display: flex;
        gap: 10px;
        margin-top: 20px;
      }
    `;
    document.head.appendChild(style);
    
    // Event listeners for modal
    const thresholdInput = modal.querySelector('#confidenceThreshold');
    const thresholdValue = modal.querySelector('#thresholdValue');
    
    thresholdInput.addEventListener('input', (e) => {
      thresholdValue.textContent = `${(e.target.value * 100).toFixed(0)}%`;
    });
    
    modal.querySelector('#saveSettings').addEventListener('click', async () => {
      const newSettings = {
        confidenceThreshold: parseFloat(thresholdInput.value),
        windowSize: parseInt(modal.querySelector('#windowSize').value),
        monitoringEnabled: modal.querySelector('#monitoringEnabled').checked
      };
      
      await chrome.runtime.sendMessage({
        action: 'UPDATE_SETTINGS',
        settings: newSettings
      });
      
      document.body.removeChild(modal);
      document.head.removeChild(style);
    });
    
    modal.querySelector('#closeModal').addEventListener('click', () => {
      document.body.removeChild(modal);
      document.head.removeChild(style);
    });
  }
}

// Initialize popup controller when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new PopupController();
});