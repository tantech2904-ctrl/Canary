// simple-chart.js - Lightweight charting for dashboard

class SimpleChart {
  constructor(canvasId, options = {}) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.data = [];
    this.options = {
      type: 'line',
      color: '#667eea',
      backgroundColor: 'rgba(102, 126, 234, 0.1)',
      lineWidth: 2,
      pointRadius: 3,
      ...options
    };
    
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }
  
  resizeCanvas() {
    const container = this.canvas.parentElement;
    this.canvas.width = container.clientWidth;
    this.canvas.height = container.clientHeight;
    this.render();
  }
  
  setData(data) {
    this.data = data;
    this.render();
  }
  
  render() {
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    const data = this.data;
    
    if (!data || data.length === 0) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw grid
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    
    // Vertical grid
    for (let i = 0; i <= 10; i++) {
      const x = (i / 10) * width;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    
    // Horizontal grid
    for (let i = 0; i <= 10; i++) {
      const y = (i / 10) * height;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
    
    // Find min and max values
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    
    // Draw line
    ctx.beginPath();
    ctx.strokeStyle = this.options.color;
    ctx.lineWidth = this.options.lineWidth;
    ctx.lineJoin = 'round';
    
    for (let i = 0; i < data.length; i++) {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((data[i] - min) / range) * height;
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    
    ctx.stroke();
    
    // Draw points
    ctx.fillStyle = this.options.color;
    for (let i = 0; i < data.length; i++) {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((data[i] - min) / range) * height;
      
      ctx.beginPath();
      ctx.arc(x, y, this.options.pointRadius, 0, Math.PI * 2);
      ctx.fill();
    }
    
    // Draw area under line
    if (this.options.type === 'line') {
      ctx.beginPath();
      ctx.moveTo(0, height);
      
      for (let i = 0; i < data.length; i++) {
        const x = (i / (data.length - 1)) * width;
        const y = height - ((data[i] - min) / range) * height;
        ctx.lineTo(x, y);
      }
      
      ctx.lineTo(width, height);
      ctx.closePath();
      ctx.fillStyle = this.options.backgroundColor;
      ctx.fill();
    }
    
    // Draw labels
    ctx.fillStyle = '#4a5568';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    
    // Bottom label
    ctx.fillText(`Min: ${min.toFixed(1)}`, 40, height - 10);
    ctx.fillText(`Max: ${max.toFixed(1)}`, width - 40, height - 10);
    ctx.fillText(`Data points: ${data.length}`, width / 2, height - 10);
  }
}

// Initialize charts on dashboard load
function initializeCharts() {
  window.memoryChart = new SimpleChart('memoryChart', {
    color: '#667eea',
    backgroundColor: 'rgba(102, 126, 234, 0.2)'
  });
  
  window.cpuChart = new SimpleChart('cpuChart', {
    color: '#f56565',
    backgroundColor: 'rgba(245, 101, 101, 0.2)'
  });
  
  // Load sample data for testing
  const sampleData = Array.from({length: 20}, (_, i) => 
    30 + Math.sin(i * 0.5) * 20 + Math.random() * 10
  );
  
  memoryChart.setData(sampleData);
  cpuChart.setData(sampleData.map(v => v * 0.8));
}

// Export for use
window.SimpleChart = SimpleChart;
window.initializeCharts = initializeCharts;