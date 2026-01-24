// Background service worker for RegimeShift Sentinel

class RegimeShiftSentinel {
  constructor() {
    this.metrics = [];
    this.currentMode = 'adaptive_observation';
    this.confidenceThreshold = 0.75;
    this.windowSize = 50;
    this.stabilizationActive = false;
    this.isInitialized = false;
    
    // Bind methods to maintain 'this' context
    this.collectMetrics = this.collectMetrics.bind(this);
    this.analyzeMetrics = this.analyzeMetrics.bind(this);
    this.handleMessage = this.handleMessage.bind(this);
    this.handleAlarm = this.handleAlarm.bind(this);
    
    this.initialize();
  }

  async initialize() {
    try {
      console.log('RegimeShift Sentinel initializing...');
      
      // Load settings from storage
      const settings = await chrome.storage.local.get([
        'confidenceThreshold',
        'windowSize',
        'monitoringEnabled'
      ]);
      
      if (settings.confidenceThreshold) {
        this.confidenceThreshold = settings.confidenceThreshold;
      }
      
      if (settings.windowSize) {
        this.windowSize = settings.windowSize;
      }
      
      // Set up alarms for periodic analysis
      await this.setupAlarms();
      
      // Listen for messages from popup
      chrome.runtime.onMessage.addListener(this.handleMessage);
      
      // Start monitoring
      this.startMonitoring();
      
      this.isInitialized = true;
      console.log('RegimeShift Sentinel initialized successfully');
      
    } catch (error) {
      console.error('Failed to initialize RegimeShift Sentinel:', error);
    }
  }

  async setupAlarms() {
    try {
      // Clear any existing alarms first
      await chrome.alarms.clearAll();
      
      // Set up alarms for periodic analysis
      await chrome.alarms.create('collectMetrics', { periodInMinutes: 0.1 }); // Every 6 seconds
      await chrome.alarms.create('analyzeMetrics', { periodInMinutes: 0.5 }); // Every 30 seconds
      
      // Listen for alarms
      chrome.alarms.onAlarm.addListener(this.handleAlarm);
      
    } catch (error) {
      console.error('Failed to setup alarms:', error);
    }
  }

  handleAlarm(alarm) {
    try {
      if (alarm.name === 'collectMetrics') {
        this.collectMetrics();
      } else if (alarm.name === 'analyzeMetrics') {
        this.analyzeMetrics();
      }
    } catch (error) {
      console.error('Error handling alarm:', error);
    }
  }

  async collectMetrics() {
    try {
      const metrics = {
        timestamp: Date.now(),
        memory: await this.getMemoryInfo(),
        cpu: await this.getCpuInfo(),
        tabs: await this.getTabInfo(),
        network: await this.getNetworkInfo()
      };
      
      this.metrics.push(metrics);
      
      // Keep only the last windowSize metrics
      if (this.metrics.length > this.windowSize) {
        this.metrics = this.metrics.slice(-this.windowSize);
      }
      
      // Store metrics for popup
      await chrome.storage.local.set({ currentMetrics: metrics });
      
    } catch (error) {
      console.error('Error collecting metrics:', error);
    }
  }

  async getMemoryInfo() {
    try {
      if (chrome.system && chrome.system.memory) {
        const memory = await chrome.system.memory.getInfo();
        return {
          available: memory.availableCapacity,
          capacity: memory.capacity,
          usage: ((memory.capacity - memory.availableCapacity) / memory.capacity) * 100
        };
      }
    } catch (error) {
      console.warn('Could not get memory info, using fallback:', error);
    }
    
    // Fallback - simulate some data
    return { 
      available: 8000000000, // 8GB
      capacity: 16000000000, // 16GB
      usage: 30 + Math.random() * 40 // 30-70%
    };
  }

  async getCpuInfo() {
    try {
      if (chrome.system && chrome.system.cpu) {
        const cpu = await chrome.system.cpu.getInfo();
        return {
          processors: cpu.numOfProcessors,
          usage: Math.random() * 100 // Simplified for now
        };
      }
    } catch (error) {
      console.warn('Could not get CPU info, using fallback:', error);
    }
    
    // Fallback
    return { 
      processors: navigator.hardwareConcurrency || 8,
      usage: 20 + Math.random() * 50 // 20-70%
    };
  }

  async getTabInfo() {
    try {
      const tabs = await chrome.tabs.query({});
      return {
        count: tabs.length,
        active: tabs.filter(t => t.active).length
      };
    } catch (error) {
      console.error('Error getting tab info:', error);
      return { count: 0, active: 0 };
    }
  }

  async getNetworkInfo() {
    return {
      online: navigator.onLine,
      type: 'unknown'
    };
  }

  async analyzeMetrics() {
    if (this.metrics.length < 5) { // Reduced from 10 for faster testing
      // Not enough data yet
      console.log('Not enough metrics yet:', this.metrics.length);
      return;
    }
    
    try {
      // Extract time series for analysis
      const memoryUsage = this.metrics.map(m => m.memory.usage);
      const cpuUsage = this.metrics.map(m => m.cpu.usage);
      
      // Run Bayesian Change-Point Detection
      const memoryShift = this.detectChangePoint(memoryUsage);
      const cpuShift = this.detectChangePoint(cpuUsage);
      
      // Check for regime shifts
      const detectedShifts = [];
      
      if (memoryShift.probability > this.confidenceThreshold) {
        detectedShifts.push({
          metric: 'memory_usage',
          probability: memoryShift.probability,
          changePoint: memoryShift.changePoint,
          severity: this.calculateSeverity(memoryShift.magnitude)
        });
      }
      
      if (cpuShift.probability > this.confidenceThreshold) {
        detectedShifts.push({
          metric: 'cpu_usage',
          probability: cpuShift.probability,
          changePoint: cpuShift.changePoint,
          severity: this.calculateSeverity(cpuShift.magnitude)
        });
      }
      
      // Handle detected shifts
      if (detectedShifts.length > 0) {
        console.log('Detected regime shifts:', detectedShifts);
        await this.handleRegimeShift(detectedShifts);
      } else {
        // Adaptive observation mode
        this.currentMode = 'adaptive_observation';
        await this.updateMode();
      }
      
    } catch (error) {
      console.error('Error analyzing metrics:', error);
    }
  }

  detectChangePoint(timeSeries) {
    // Implement Bayesian Change-Point Detection
    // This is a simplified version - you can integrate a full BCPD library
    
    if (!timeSeries || timeSeries.length < 2) {
      return { probability: 0, changePoint: -1, magnitude: 0 };
    }
    
    // Calculate mean and variance for different segments
    const n = timeSeries.length;
    let maxProbability = 0;
    let bestChangePoint = -1;
    
    for (let i = 3; i < n - 3; i++) { // Reduced window for faster processing
      const segment1 = timeSeries.slice(0, i);
      const segment2 = timeSeries.slice(i);
      
      const mean1 = this.mean(segment1);
      const mean2 = this.mean(segment2);
      const var1 = this.variance(segment1, mean1);
      const var2 = this.variance(segment2, mean2);
      
      // Simplified Bayesian probability calculation
      const probability = Math.min(
        0.95,
        Math.abs(mean1 - mean2) / (Math.sqrt(var1 + var2) + 0.001)
      );
      
      if (probability > maxProbability) {
        maxProbability = probability;
        bestChangePoint = i;
      }
    }
    
    return {
      probability: maxProbability,
      changePoint: bestChangePoint,
      magnitude: maxProbability
    };
  }

  mean(arr) {
    if (!arr || arr.length === 0) return 0;
    return arr.reduce((a, b) => a + b, 0) / arr.length;
  }

  variance(arr, mean) {
    if (!arr || arr.length === 0) return 0;
    return arr.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / arr.length;
  }

  calculateSeverity(magnitude) {
    if (magnitude > 0.8) return 'critical';
    if (magnitude > 0.6) return 'high';
    if (magnitude > 0.4) return 'medium';
    return 'low';
  }

  async handleRegimeShift(shifts) {
    try {
      this.currentMode = 'warning';
      
      // Store warning info for popup
      const warning = {
        timestamp: Date.now(),
        shifts: shifts,
        overallConfidence: Math.max(...shifts.map(s => s.probability))
      };
      
      await chrome.storage.local.set({ 
        currentWarning: warning,
        currentMode: this.currentMode 
      });
      
      // Send notification
      this.sendNotification(warning);
      
      console.log('Regime shift warning stored:', warning);
      
    } catch (error) {
      console.error('Error handling regime shift:', error);
    }
  }

  async sendNotification(warning) {
    try {
      // Create browser notification
      await chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon128.png',
        title: '🚨 Regime Shift Detected',
        message: `System behavior change detected with ${(warning.overallConfidence * 100).toFixed(1)}% confidence`,
        priority: 2
      });
      
      // Listen for notification clicks
      chrome.notifications.onClicked.addListener((notificationId) => {
        chrome.tabs.create({ url: chrome.runtime.getURL('dashboard.html') });
      });
      
    } catch (error) {
      console.error('Error sending notification:', error);
    }
  }

  async enterStabilizationMode() {
    try {
      this.currentMode = 'stabilization';
      this.stabilizationActive = true;
      
      await chrome.storage.local.set({ 
        currentMode: this.currentMode,
        stabilizationActive: true 
      });
      
      // Implement stabilization actions
      await this.performStabilizationActions();
      
      console.log('Entered stabilization mode');
      
    } catch (error) {
      console.error('Error entering stabilization mode:', error);
    }
  }

  async performStabilizationActions() {
    console.log('Performing stabilization actions...');
    
    try {
      // 1. Reduce tab activity
      const tabs = await chrome.tabs.query({});
      let discarded = 0;
      
      for (const tab of tabs) {
        if (!tab.active && !tab.pinned && tab.id) {
          try {
            await chrome.tabs.discard(tab.id);
            discarded++;
          } catch (error) {
            console.warn('Could not discard tab:', tab.id, error);
          }
        }
      }
      
      console.log(`Discarded ${discarded} inactive tabs`);
      
      // Set timeout to exit stabilization mode
      setTimeout(() => {
        this.exitStabilizationMode();
      }, 2 * 60 * 1000); // Reduced to 2 minutes for testing
      
    } catch (error) {
      console.error('Error performing stabilization actions:', error);
    }
  }

  async exitStabilizationMode() {
    try {
      this.stabilizationActive = false;
      this.currentMode = 'adaptive_observation';
      
      await chrome.storage.local.set({ 
        currentMode: this.currentMode,
        stabilizationActive: false 
      });
      
      console.log('Exited stabilization mode');
      
    } catch (error) {
      console.error('Error exiting stabilization mode:', error);
    }
  }

  async updateMode() {
    try {
      await chrome.storage.local.set({ currentMode: this.currentMode });
    } catch (error) {
      console.error('Error updating mode:', error);
    }
  }

  async handleMessage(request, sender, sendResponse) {
    console.log('Received message:', request.action);
    
    // Always respond asynchronously
    setTimeout(async () => {
      try {
        let response;
        
        switch (request.action) {
          case 'GET_METRICS':
            response = { metrics: this.metrics };
            break;
            
          case 'GET_STATUS':
            response = {
              mode: this.currentMode,
              stabilizationActive: this.stabilizationActive,
              metricsCount: this.metrics.length,
              isInitialized: this.isInitialized
            };
            break;
            
          case 'TRIGGER_STABILIZATION':
            await this.enterStabilizationMode();
            response = { success: true };
            break;
            
          case 'ACKNOWLEDGE_WARNING':
            // Clear current warning
            await chrome.storage.local.remove('currentWarning');
            this.currentMode = 'adaptive_observation';
            await this.updateMode();
            response = { success: true };
            break;
            
          case 'GET_SETTINGS':
            const settings = await chrome.storage.local.get([
              'confidenceThreshold',
              'windowSize',
              'monitoringEnabled'
            ]);
            response = settings;
            break;
            
          case 'UPDATE_SETTINGS':
            await chrome.storage.local.set(request.settings);
            
            // Update internal state
            if (request.settings.confidenceThreshold !== undefined) {
              this.confidenceThreshold = request.settings.confidenceThreshold;
            }
            if (request.settings.windowSize !== undefined) {
              this.windowSize = request.settings.windowSize;
            }
            
            response = { success: true };
            break;
            
          case 'TEST_WARNING':
            // For testing - create a fake warning
            await this.handleRegimeShift([{
              metric: 'test_usage',
              probability: 0.85,
              changePoint: 5,
              severity: 'high'
            }]);
            response = { success: true, message: 'Test warning created' };
            break;
            
          case 'CLEAR_DATA':
            // For testing - clear all data
            this.metrics = [];
            await chrome.storage.local.clear();
            response = { success: true, message: 'Data cleared' };
            break;
            
          default:
            response = { error: 'Unknown action' };
        }
        
        sendResponse(response);
        
      } catch (error) {
        console.error('Error handling message:', error);
        sendResponse({ error: error.message });
      }
    }, 0);
    
    // Return true to indicate we'll respond asynchronously
    return true;
  }

  startMonitoring() {
    try {
      // Initial metrics collection
      this.collectMetrics();
      
      // Start analysis after a delay
      setTimeout(() => {
        this.analyzeMetrics();
      }, 5000); // Reduced to 5 seconds for testing
      
      console.log('Monitoring started');
      
    } catch (error) {
      console.error('Error starting monitoring:', error);
    }
  }
}

// Initialize the sentinel
let sentinel;

try {
  sentinel = new RegimeShiftSentinel();
  console.log('RegimeShift Sentinel instance created');
} catch (error) {
  console.error('Failed to create RegimeShift Sentinel:', error);
}

// Export for testing
if (typeof window !== 'undefined') {
  window.RegimeShiftSentinel = RegimeShiftSentinel;
  window.sentinel = sentinel;
}