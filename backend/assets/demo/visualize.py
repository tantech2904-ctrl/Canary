"""
Visualization utilities for demonstration
"""

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_regime_comparison(data_dict, titles=None, figsize=(15, 10)):
    """
    Plot multiple time series with regime shifts for comparison.
    
    Args:
        data_dict: Dictionary of {name: data_array}
        titles: Titles for each subplot
        figsize: Figure size
    """
    n_plots = len(data_dict)
    
    if titles is None:
        titles = list(data_dict.keys())
    
    fig, axes = plt.subplots(n_plots, 1, figsize=figsize, sharex=True)
    
    if n_plots == 1:
        axes = [axes]
    
    for idx, (name, data) in enumerate(data_dict.items()):
        ax = axes[idx]
        ax.plot(data, 'b-', alpha=0.7, linewidth=1)
        ax.set_ylabel('Value', fontsize=12)
        ax.set_title(titles[idx], fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('Time', fontsize=12)
    plt.tight_layout()
    return fig

def create_3d_visualization(data, probabilities, change_points):
    """
    Create 3D visualization of time series with probabilities.
    
    Args:
        data: Time series data
        probabilities: Change point probabilities
        change_points: Detected change points
        
    Returns:
        Plotly 3D figure
    """
    time = np.arange(len(data))
    
    fig = go.Figure(data=[
        go.Scatter3d(
            x=time,
            y=data,
            z=probabilities,
            mode='lines',
            line=dict(
                width=3,
                color=probabilities,
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="Probability")
            ),
            name='Time Series'
        ),
        go.Scatter3d(
            x=change_points,
            y=data[change_points],
            z=probabilities[change_points],
            mode='markers',
            marker=dict(
                size=8,
                color='red',
                symbol='diamond'
            ),
            name='Change Points'
        )
    ])
    
    fig.update_layout(
        title="3D Visualization: Data vs Probability",
        scene=dict(
            xaxis_title='Time',
            yaxis_title='Data Value',
            zaxis_title='Change Probability',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        height=600
    )
    
    return fig

def plot_early_warning_signals(signals_dict, figsize=(12, 8)):
    """
    Plot early warning signals.
    
    Args:
        signals_dict: Dictionary of signal data
        figsize: Figure size
        
    Returns:
        Matplotlib figure
    """
    n_signals = len(signals_dict)
    
    fig, axes = plt.subplots(n_signals, 1, figsize=figsize, sharex=True)
    
    if n_signals == 1:
        axes = [axes]
    
    for idx, (signal_name, signal_data) in enumerate(signals_dict.items()):
        ax = axes[idx]
        
        if isinstance(signal_data, dict) and 'values' in signal_data:
            values = signal_data['values']
            time = np.linspace(0, len(values) * 10, len(values))  # Approximate time
            
            ax.plot(time, values, 'g-', alpha=0.7, linewidth=2)
            
            if 'threshold' in signal_data:
                ax.axhline(y=signal_data['threshold'], color='r', linestyle='--', alpha=0.5)
            
            if 'trend' in signal_data:
                trend_line = np.polyval([signal_data['trend'], np.mean(values)], 
                                      np.arange(len(values)))
                ax.plot(time, trend_line, 'b--', alpha=0.5, linewidth=1)
        
        ax.set_ylabel(signal_name.replace('_', ' ').title(), fontsize=11)
        ax.grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('Time', fontsize=12)
    fig.suptitle('Early Warning Signals', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    return fig

def create_radar_chart(metrics_dict, title="System Health Radar"):
    """
    Create radar chart for system metrics.
    
    Args:
        metrics_dict: Dictionary of metric values
        title: Chart title
        
    Returns:
        Plotly radar chart figure
    """
    categories = list(metrics_dict.keys())
    values = list(metrics_dict.values())
    
    # Close the radar chart
    categories = categories + [categories[0]]
    values = values + [values[0]]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line=dict(color='blue', width=2),
        opacity=0.7
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        title=title,
        showlegend=False,
        height=400
    )
    
    return fig

def plot_probability_distribution(probabilities, figsize=(10, 6)):
    """
    Plot probability distribution and cumulative distribution.
    
    Args:
        probabilities: Array of probabilities
        figsize: Figure size
        
    Returns:
        Matplotlib figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Histogram
    ax1.hist(probabilities, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    ax1.axvline(x=0.5, color='red', linestyle='--', alpha=0.7, label='Threshold')
    ax1.set_xlabel('Probability', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title('Probability Distribution', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Cumulative distribution
    sorted_probs = np.sort(probabilities)
    cdf = np.arange(1, len(sorted_probs) + 1) / len(sorted_probs)
    
    ax2.plot(sorted_probs, cdf, 'b-', linewidth=2)
    ax2.axvline(x=0.5, color='red', linestyle='--', alpha=0.7)
    ax2.set_xlabel('Probability', fontsize=12)
    ax2.set_ylabel('Cumulative Probability', fontsize=12)
    ax2.set_title('Cumulative Distribution', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Example usage
    print("Visualization utilities loaded.")
    print("Available functions:")
    print("- plot_regime_comparison")
    print("- create_3d_visualization")
    print("- plot_early_warning_signals")
    print("- create_radar_chart")
    print("- plot_probability_distribution")