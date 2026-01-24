"""
Utility functions for RegimeShift Sentinel
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional, Any
import json
import yaml
from datetime import datetime
import warnings

def load_metrics(filepath: str, metric_col: Optional[str] = None) -> np.ndarray:
    """
    Load metrics from CSV file.
    
    Args:
        filepath: Path to CSV file
        metric_col: Column name to load (if None, loads first numeric column)
        
    Returns:
        Array of metric values
    """
    df = pd.read_csv(filepath)
    
    if metric_col is None:
        # Find first numeric column
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            metric_col = numeric_cols[0]
        else:
            raise ValueError("No numeric columns found in CSV")
    
    if metric_col not in df.columns:
        raise ValueError(f"Column '{metric_col}' not found in CSV")
    
    values = df[metric_col].values
    
    # Handle missing values
    if np.any(np.isnan(values)):
        warnings.warn(f"Found {np.sum(np.isnan(values))} NaN values. Interpolating.")
        values = pd.Series(values).interpolate().fillna(method='bfill').fillna(method='ffill').values
    
    return values

def save_results(results: Dict, filepath: str):
    """
    Save detection results to JSON file.
    
    Args:
        results: Results dictionary
        filepath: Path to save JSON
    """
    # Convert numpy arrays to lists for JSON serialization
    def convert_for_json(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_for_json(item) for item in obj]
        else:
            return obj
    
    results_json = convert_for_json(results)
    
    with open(filepath, 'w') as f:
        json.dump(results_json, f, indent=2)
    
    print(f"Results saved to {filepath}")

def load_results(filepath: str) -> Dict:
    """
    Load results from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Results dictionary
    """
    with open(filepath, 'r') as f:
        results = json.load(f)
    
    return results

def plot_timeseries(data: np.ndarray, 
                   change_points: Optional[np.ndarray] = None,
                   probabilities: Optional[np.ndarray] = None,
                   title: str = "Time Series with Change Points",
                   save_path: Optional[str] = None,
                   show_plot: bool = True) -> plt.Figure:
    """
    Plot time series with detected change points.
    
    Args:
        data: Time series data
        change_points: Indices of detected change points
        probabilities: Change point probabilities over time
        title: Plot title
        save_path: Path to save figure (if None, don't save)
        show_plot: Whether to display plot
        
    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(2 if probabilities is not None else 1, 1, 
                           figsize=(12, 8 if probabilities is not None else 6),
                           sharex=True)
    
    if probabilities is not None:
        ax1, ax2 = axes
    else:
        ax1 = axes
        ax2 = None
    
    # Plot time series
    time = np.arange(len(data))
    ax1.plot(time, data, 'b-', alpha=0.7, linewidth=1, label='Data')
    
    # Highlight change points
    if change_points is not None and len(change_points) > 0:
        for cp in change_points:
            if cp < len(data):
                ax1.axvline(x=cp, color='r', linestyle='--', alpha=0.7, linewidth=1)
        
        # Add shaded regions between change points
        cps = [0] + change_points.tolist() + [len(data)]
        colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightpink']
        for i in range(len(cps) - 1):
            start, end = cps[i], cps[i+1]
            if end > start:
                ax1.axvspan(start, end, alpha=0.2, color=colors[i % len(colors)])
    
    ax1.set_ylabel('Value', fontsize=12)
    ax1.set_title(title, fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot probabilities if provided
    if probabilities is not None:
        ax2.plot(time, probabilities, 'g-', alpha=0.7, linewidth=1.5, label='Change Probability')
        ax2.axhline(y=0.5, color='r', linestyle='--', alpha=0.5, linewidth=1, label='Threshold (0.5)')
        ax2.set_ylabel('Probability', fontsize=12)
        ax2.set_xlabel('Time', fontsize=12)
        ax2.set_ylim(-0.05, 1.05)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    if show_plot:
        plt.show()
    
    return fig

def create_interactive_plot(data: np.ndarray,
                          change_points: Optional[np.ndarray] = None,
                          probabilities: Optional[np.ndarray] = None,
                          early_warnings: Optional[Dict] = None,
                          title: str = "Interactive Analysis") -> go.Figure:
    """
    Create interactive Plotly visualization.
    
    Args:
        data: Time series data
        change_points: Detected change points
        probabilities: Change probabilities
        early_warnings: Early warning signals
        title: Plot title
        
    Returns:
        Plotly figure
    """
    time = np.arange(len(data))
    
    # Determine number of subplots
    num_subplots = 1
    if probabilities is not None:
        num_subplots += 1
    if early_warnings is not None:
        num_subplots += len(early_warnings.get('warning_signals', {}))
    
    fig = make_subplots(
        rows=num_subplots, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=[title, "Change Probability", *list(early_warnings.get('warning_signals', {}).keys())[:num_subplots-2]]
        if num_subplots > 1 else [title]
    )
    
    # Main time series plot
    fig.add_trace(
        go.Scatter(
            x=time,
            y=data,
            mode='lines',
            name='Data',
            line=dict(color='blue', width=1),
            opacity=0.7
        ),
        row=1, col=1
    )
    
    # Add change point markers
    if change_points is not None:
        for cp in change_points:
            if cp < len(data):
                fig.add_vline(
                    x=cp,
                    line=dict(color="red", width=1, dash="dash"),
                    opacity=0.7,
                    row=1, col=1
                )
    
    # Add probability plot
    if probabilities is not None and num_subplots > 1:
        fig.add_trace(
            go.Scatter(
                x=time,
                y=probabilities,
                mode='lines',
                name='Change Probability',
                line=dict(color='green', width=2),
                fill='tozeroy',
                opacity=0.6
            ),
            row=2, col=1
        )
        
        # Add threshold line
        fig.add_hline(
            y=0.5,
            line=dict(color="red", width=1, dash="dot"),
            opacity=0.5,
            row=2, col=1
        )
    
    # Add early warning signals
    if early_warnings is not None and num_subplots > 2:
        row_idx = 3
        signals = early_warnings.get('warning_signals', {})
        
        for i, (signal_name, signal_data) in enumerate(list(signals.items())[:num_subplots-2]):
            if isinstance(signal_data, dict) and 'values' in signal_data:
                signal_vals = signal_data['values']
                signal_time = np.linspace(0, len(data), len(signal_vals))
                
                fig.add_trace(
                    go.Scatter(
                        x=signal_time,
                        y=signal_vals,
                        mode='lines',
                        name=signal_name,
                        line=dict(width=2),
                        opacity=0.8
                    ),
                    row=row_idx, col=1
                )
                
                # Add trend line if available
                if 'trend' in signal_data:
                    fig.add_hline(
                        y=signal_data['trend'],
                        line=dict(color="orange", width=1, dash="dash"),
                        opacity=0.7,
                        row=row_idx, col=1
                    )
                
                row_idx += 1
    
    # Update layout
    fig.update_layout(
        height=300 * num_subplots,
        showlegend=True,
        title_text=title,
        hovermode='x unified'
    )
    
    # Update axes
    for i in range(1, num_subplots + 1):
        fig.update_yaxes(title_text="Value" if i == 1 else "Probability" if i == 2 else "Signal", row=i, col=1)
    
    fig.update_xaxes(title_text="Time", row=num_subplots, col=1)
    
    return fig

def generate_report(results: Dict, 
                   config: Dict,
                   output_dir: str = "./reports") -> str:
    """
    Generate a comprehensive HTML report.
    
    Args:
        results: Detection results
        config: Configuration used
        output_dir: Directory to save report
        
    Returns:
        Path to generated report
    """
    import os
    from datetime import datetime
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(output_dir, f"report_{timestamp}.html")
    
    # Create HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RegimeShift Sentinel Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
            .section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .metric {{ display: inline-block; background: white; padding: 15px; 
                      margin: 10px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .change-point {{ color: #dc3545; font-weight: bold; }}
            .warning {{ color: #ffc107; font-weight: bold; }}
            .success {{ color: #28a745; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #667eea; color: white; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>RegimeShift Sentinel Report</h1>
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <div class="metric">
                <h3>Data Points Analyzed</h3>
                <p style="font-size: 24px;">{len(results.get('data', []))}</p>
            </div>
            <div class="metric">
                <h3>Change Points Detected</h3>
                <p style="font-size: 24px;" class="change-point">{len(results.get('change_points', []))}</p>
            </div>
            <div class="metric">
                <h3>Warning Score</h3>
                <p style="font-size: 24px;" class="warning">{results.get('warning_score', 0):.2f}/1.0</p>
            </div>
            <div class="metric">
                <h3>Detection Confidence</h3>
                <p style="font-size: 24px;" class="success">{results.get('average_confidence', 0):.1%}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Change Points Detected</h2>
            <table>
                <tr>
                    <th>Index</th>
                    <th>Time</th>
                    <th>Probability</th>
                    <th>Confidence</th>
                </tr>
    """
    
    # Add change point rows
    change_points = results.get('change_points', [])
    probabilities = results.get('probabilities', [])
    
    for i, cp in enumerate(change_points):
        prob = probabilities[cp] if cp < len(probabilities) else 0
        html_content += f"""
                <tr>
                    <td>{cp}</td>
                    <td>Point #{cp}</td>
                    <td>{prob:.3f}</td>
                    <td>{'High' if prob > 0.7 else 'Medium' if prob > 0.3 else 'Low'}</td>
                </tr>
        """
    
    html_content += """
            </table>
        </div>
        
        <div class="section">
            <h2>Early Warning Signals</h2>
            <table>
                <tr>
                    <th>Signal</th>
                    <th>Value</th>
                    <th>Trend</th>
                    <th>Status</th>
                </tr>
    """
    
    # Add warning signals
    warning_signals = results.get('warning_signals', {})
    for signal_name, signal_data in warning_signals.items():
        if isinstance(signal_data, dict):
            value = signal_data.get('current', 0)
            trend = signal_data.get('trend', 0)
            status = "⚠️ Warning" if trend > 0 else "✅ Stable"
            html_content += f"""
                <tr>
                    <td>{signal_name.replace('_', ' ').title()}</td>
                    <td>{value:.3f}</td>
                    <td>{trend:+.3f}</td>
                    <td>{status}</td>
                </tr>
            """
    
    html_content += """
            </table>
        </div>
        
        <div class="section">
            <h2>Configuration Used</h2>
            <pre style="background: white; padding: 15px; border-radius: 6px;">
    """
    
    html_content += json.dumps(config, indent=2)
    
    html_content += """
            </pre>
        </div>
        
        <div class="section">
            <h2>Recommended Actions</h2>
            <p>Based on the analysis, the following actions are recommended:</p>
            <ul>
                <li>Monitor the system closely for next 24 hours</li>
                <li>Review logs around detected change points</li>
                <li>Consider adjusting monitoring thresholds</li>
                <li>Implement suggested mitigations if warning score > 0.7</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Notes</h2>
            <p>This report was automatically generated by RegimeShift Sentinel v0.1.0</p>
            <p>For questions or concerns, please review the system documentation.</p>
        </div>
    </body>
    </html>
    """
    
    # Save report
    with open(report_path, 'w') as f:
        f.write(html_content)
    
    print(f"Report generated: {report_path}")
    return report_path

def validate_input(data: np.ndarray, 
                  min_length: int = 10,
                  max_length: int = 100000) -> Tuple[bool, str]:
    """
    Validate input data.
    
    Args:
        data: Input array
        min_length: Minimum required length
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, np.ndarray):
        return False, f"Data must be numpy array, got {type(data)}"
    
    if len(data.shape) != 1:
        return False, f"Data must be 1-dimensional, got shape {data.shape}"
    
    if len(data) < min_length:
        return False, f"Data too short: {len(data)} < {min_length}"
    
    if len(data) > max_length:
        return False, f"Data too long: {len(data)} > {max_length}"
    
    # Check for NaN/inf
    if np.any(np.isnan(data)):
        return False, f"Data contains NaN values"
    
    if np.any(np.isinf(data)):
        return False, f"Data contains infinite values"
    
    return True, ""

def calculate_statistics(data: np.ndarray) -> Dict:
    """
    Calculate basic statistics for data.
    
    Args:
        data: Input array
        
    Returns:
        Dictionary with statistics
    """
    return {
        'mean': float(np.mean(data)),
        'std': float(np.std(data)),
        'min': float(np.min(data)),
        'max': float(np.max(data)),
        'median': float(np.median(data)),
        'skewness': float(pd.Series(data).skew()),
        'kurtosis': float(pd.Series(data).kurtosis()),
        'length': len(data),
        'has_trend': abs(np.polyfit(np.arange(len(data)), data, 1)[0]) > 0.001
    }

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"