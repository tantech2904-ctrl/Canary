"""
Streamlit Dashboard for RegimeShift Sentinel
Interactive visualization and demonstration
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.detector import BayesianChangePointDetector
from src.early_signals import EarlyWarningAnalyzer
from src.mitigator import MitigationEngine, SystemType
from src.simulator import RegimeShiftSimulator
from src.utils import create_interactive_plot, calculate_statistics

def interpret_signal(signal_name, value):
    """Interpret signal value for display."""
    interpretations = {
        'variance_trend': f"Variance trend is {'increasing' if value > 0 else 'decreasing' if value < 0 else 'stable'} ({value:+.3f})",
        'autocorrelation_trend': f"Autocorrelation is {'increasing ' if value > 0 else 'decreasing ' if value < 0 else 'stable ↔'} ({value:+.3f})",
        'warning_score': f"{'High' if value > 0.7 else 'Medium' if value > 0.4 else 'Low'} risk level",
        'spectral_ratio': f"{'Low frequency dominant' if value > 2 else 'Balanced spectrum' if value > 0.5 else 'High frequency dominant'} ({value:.2f})",
        'trend_strength': f"Trend strength: {'Strong' if value > 0.5 else 'Moderate' if value > 0.2 else 'Weak'} ({value:.2f})",
        'residual_variance': f"Residual variance: {value:.4f}"
    }
    return interpretations.get(signal_name, f"Signal: {signal_name} = {value:.4f}")

# Page configuration
st.set_page_config(
    page_title="Canary",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .warning-card {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
    }
    .danger-card {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
    }
    .success-card {
        background: linear-gradient(135deg, #10b981 0%, #047857 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
    }
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'mitigation_actions' not in st.session_state:
    st.session_state.mitigation_actions = []
if 'approved_actions' not in st.session_state:
    st.session_state.approved_actions = []

# Header
st.markdown('<h1 class="main-header">🐤 Canary - Early Warning AI for Critical Systems</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI that sings before your system fails</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Data generation options
    dataset_type = st.selectbox(
        "Dataset Type",
        ["complex", "mean_shift", "variance_shift", "ml_training"],
        help="Type of regime shifts to simulate"
    )
    
    n_samples = st.slider(
        "Number of Samples",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100
    )
    
    add_outliers = st.checkbox("Add Outliers", value=True)
    add_missing = st.checkbox("Add Missing Values", value=False)
    
    if st.button("🎲 Generate New Data", use_container_width=True):
        with st.spinner("Generating data..."):
            simulator = RegimeShiftSimulator(seed=42)
            df = simulator.generate_dataset(
                n_samples=n_samples,
                dataset_type=dataset_type,
                add_outliers=add_outliers,
                add_missing=add_missing
            )
            st.session_state.data = df
            st.session_state.results = None
            st.session_state.mitigation_actions = []
            st.success("Data generated successfully!")
    
    # Detection parameters
    st.markdown("### 🔍 Detection Parameters")
    hazard_rate = st.slider(
        "Hazard Rate (1/λ)",
        min_value=0.001,
        max_value=0.1,
        value=0.02,
        step=0.001,
        format="%.3f",
        help="Expected time between change points"
    )
    
    threshold = st.slider(
        "Probability Threshold",
        min_value=0.1,
        max_value=0.9,
        value=0.5,
        step=0.05,
        help="Threshold for declaring change point"
    )
    
    # System type for mitigation
    st.markdown("### 🛡️ Mitigation Settings")
    system_type = st.selectbox(
        "System Type",
        [t.value for t in SystemType],
        index=0
    )
    
    risk_tolerance = st.select_slider(
        "Risk Tolerance",
        options=["low", "medium", "high"],
        value="medium"
    )

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📈 Visualization", "🔬 Analysis", "🛡️ Mitigation", "📋 Report"])

with tab1:
    st.markdown("## 📊 Data Visualization")
    
    if st.session_state.data is not None:
        df = st.session_state.data
        
        # Display data info
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Samples", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            st.metric("Numeric Columns", len(numeric_cols))
        with col4:
            missing = df.isna().sum().sum()
            st.metric("Missing Values", missing)
        
        # Select column to analyze
        if len(numeric_cols) > 0:
            selected_col = st.selectbox(
                "Select metric to analyze",
                numeric_cols,
                key="vis_col_select"
            )
            
            # Get data
            data = df[selected_col].values
            if np.any(np.isnan(data)):
                data = pd.Series(data).interpolate().fillna(method='bfill').fillna(method='ffill').values
            
            # Raw data plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=data,
                mode='lines',
                name=selected_col,
                line=dict(color='blue', width=1)
            ))
            
            fig.update_layout(
                title=f"Raw Data: {selected_col}",
                xaxis_title="Time",
                yaxis_title="Value",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics
            st.markdown("### 📊 Statistics")
            stats = calculate_statistics(data)
            
            stat_cols = st.columns(4)
            with stat_cols[0]:
                st.metric("Mean", f"{stats['mean']:.3f}")
            with stat_cols[1]:
                st.metric("Std Dev", f"{stats['std']:.3f}")
            with stat_cols[2]:
                st.metric("Min/Max", f"{stats['min']:.3f}/{stats['max']:.3f}")
            with stat_cols[3]:
                st.metric("Has Trend", "📈 Yes" if stats['has_trend'] else "➡️ No")
        else:
            st.warning("No numeric columns found in the data!")
    else:
        st.info("👈 Generate data using the sidebar to get started!")

with tab2:
    st.markdown("## 🔬 Change Point Analysis")
    
    if st.session_state.data is not None:
        df = st.session_state.data
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            selected_col = st.selectbox(
                "Select metric to analyze",
                numeric_cols,
                key="analysis_col_select"
            )
            
            # Get data
            data = df[selected_col].values
            if np.any(np.isnan(data)):
                data = pd.Series(data).interpolate().fillna(method='bfill').fillna(method='ffill').values
            
            # Run detection
            if st.button("🚀 Run Detection", type="primary", use_container_width=True):
                with st.spinner("Analyzing time series..."):
                    # Initialize detectors
                    detector = BayesianChangePointDetector(
                        hazard_rate=hazard_rate,
                        threshold=threshold
                    )
                    
                    early_warning = EarlyWarningAnalyzer()
                    
                    # Run detection
                    results = detector.detect_offline(data)
                    
                    # Early warning analysis
                    is_warning, warning_score, warning_signals = early_warning.predict_regime_shift(data)
                    
                    # Store results
                    st.session_state.results = {
                        'detection': results,
                        'early_warning': {
                            'is_warning': is_warning,
                            'warning_score': warning_score,
                            'signals': warning_signals
                        },
                        'config': {
                            'hazard_rate': hazard_rate,
                            'threshold': threshold
                        }
                    }
                    
                    # Generate mitigation suggestions
                    mitigator = MitigationEngine()
                    severity = warning_score
                    issue_type = "variance_spike" if warning_signals.get('variance_trend', 0) > 0 else "regime_shift"
                    
                    actions = mitigator.suggest_actions(
                        system_type=system_type,
                        issue_type=issue_type,
                        severity=severity,
                        context={"capabilities": ["training_in_progress", "has_learning_rate_control"]}
                    )
                    
                    st.session_state.mitigation_actions = actions
                    
                    st.success("Analysis complete!")
            
            # Display results if available
            if st.session_state.results is not None:
                results = st.session_state.results
                detection = results['detection']
                early_warning = results['early_warning']
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    change_points = detection['change_points']
                    st.metric(
                        "Change Points",
                        len(change_points),
                        delta=f"{len(change_points)/len(data)*100:.1f}% of series"
                    )
                
                with col2:
                    avg_prob = np.mean(detection['probabilities'])
                    st.metric(
                        "Avg Probability",
                        f"{avg_prob:.3f}",
                        delta="High" if avg_prob > 0.5 else "Low"
                    )
                
                with col3:
                    warning_score = early_warning['warning_score']
                    warning_color = "🟢" if warning_score < 0.4 else "🟡" if warning_score < 0.7 else "🔴"
                    st.metric(
                        "Warning Score",
                        f"{warning_score:.2f}",
                        delta=f"{warning_color} {'Low' if warning_score < 0.4 else 'Medium' if warning_score < 0.7 else 'High'}"
                    )
                
                with col4:
                    is_warning = early_warning['is_warning']
                    st.metric(
                        "Status",
                        "⚠️ Warning" if is_warning else "✅ Stable",
                        delta="Take action" if is_warning else "Monitor"
                    )
                
                # Interactive plot
                st.markdown("### 📈 Interactive Analysis")
                
                fig = create_interactive_plot(
                    data=detection['data'],
                    change_points=detection['change_points'],
                    probabilities=detection['probabilities'],
                    early_warnings=early_warning
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Early warning signals
                st.markdown("### 📡 Early Warning Signals")
                
                if 'signals' in early_warning:
                    signals = early_warning['signals']
                    
                    # Create columns for signal cards
                    sig_cols = st.columns(4)
                    signal_keys = list(signals.keys())
                    
                    for i, sig_key in enumerate(signal_keys[:4]):
                        with sig_cols[i]:
                            if sig_key in ['variance_trend', 'autocorrelation_trend']:
                                value = signals[sig_key]
                                delta = f"{value:+.3f}"
                                title = sig_key.replace('_', ' ').title()
                                
                                if sig_key == 'variance_trend':
                                    st.metric(
                                        title,
                                        "📈" if value > 0 else "📉",
                                        delta=delta
                                    )
                                else:
                                    st.metric(
                                        title,
                                        "📈" if value > 0 else "📉",
                                        delta=delta
                                    )
                    
                    # Detailed signal table
                    with st.expander("View Detailed Signals"):
                        signal_data = []
                        for key, value in signals.items():
                            if isinstance(value, (int, float, np.number)):
                                signal_data.append({
                                    "Signal": key.replace('_', ' ').title(),
                                    "Value": f"{value:.4f}",
                                    "Interpretation":interpret_signal(key, value)
                                })
                        
                        if signal_data:
                            st.table(pd.DataFrame(signal_data))
                
                # Change point table
                st.markdown("### 🎯 Detected Change Points")
                
                if len(change_points) > 0:
                    cp_data = []
                    for i, cp in enumerate(change_points):
                        if cp < len(detection['probabilities']):
                            prob = detection['probabilities'][cp]
                            cp_data.append({
                                "#": i+1,
                                "Index": cp,
                                "Time": f"Point {cp}",
                                "Probability": f"{prob:.3f}",
                                "Confidence": "High" if prob > 0.7 else "Medium" if prob > 0.3 else "Low"
                            })
                    
                    st.table(pd.DataFrame(cp_data))
                else:
                    st.info("No change points detected with current threshold.")
        else:
            st.warning("No numeric columns found in the data!")
    else:
        st.info("👈 Generate data and run analysis to see results!")

with tab3:
    st.markdown("## 🛡️ Mitigation Actions")
    
    if st.session_state.mitigation_actions:
        actions = st.session_state.mitigation_actions
        results = st.session_state.results
        
        st.markdown(f"### 💡 Suggested Actions for {system_type.replace('_', ' ').title()}")
        st.markdown(f"*Warning Score: {results['early_warning']['warning_score']:.2f}*")
        
        # Display actions
        for i, action in enumerate(actions):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Risk badge
                    risk_color = {
                        "low": "🟢",
                        "medium": "🟡", 
                        "high": "🔴"
                    }.get(action.risk_level.value, "⚪")
                    
                    st.markdown(f"#### {risk_color} {action.description}")
                    st.markdown(f"**Command:** `{action.command}`")
                    
                    # Metrics
                    metric_cols = st.columns(4)
                    with metric_cols[0]:
                        st.metric("Confidence", f"{action.confidence:.0%}")
                    with metric_cols[1]:
                        st.metric("Risk", action.risk_level.value.title())
                    with metric_cols[2]:
                        st.metric("Time", f"{action.estimated_time:.0f}s")
                    with metric_cols[3]:
                        st.metric("Reversibility", f"{action.reversibility:.0%}")
                
                with col2:
                    action_id = f"action_{i}"
                    if st.button("✅ Approve", key=f"approve_{action_id}", use_container_width=True):
                        st.session_state.approved_actions.append({
                            "action": action,
                            "timestamp": datetime.now(),
                            "status": "approved"
                        })
                        st.success(f"Approved: {action.description}")
                        st.rerun()
                    
                    if st.button("❌ Reject", key=f"reject_{action_id}", use_container_width=True):
                        st.session_state.approved_actions.append({
                            "action": action,
                            "timestamp": datetime.now(),
                            "status": "rejected"
                        })
                        st.warning(f"Rejected: {action.description}")
                        st.rerun()
                
                st.divider()
        
        # Approved actions history
        if st.session_state.approved_actions:
            st.markdown("### 📋 Approval History")
            
            history_data = []
            for item in st.session_state.approved_actions:
                history_data.append({
                    "Time": item["timestamp"].strftime("%H:%M:%S"),
                    "Action": item["action"].description[:50] + "...",
                    "Risk": item["action"].risk_level.value.title(),
                    "Status": item["status"].title()
                })
            
            st.table(pd.DataFrame(history_data))
            
            # Execute all approved actions
            if st.button("🚀 Execute All Approved Actions", type="primary", use_container_width=True):
                approved = [a for a in st.session_state.approved_actions if a["status"] == "approved"]
                if approved:
                    with st.spinner(f"Executing {len(approved)} actions..."):
                        # Simulate execution
                        import time
                        progress_bar = st.progress(0)
                        
                        for i, item in enumerate(approved):
                            time.sleep(0.5)  # Simulate execution time
                            progress_bar.progress((i + 1) / len(approved))
                        
                        st.success(f"Successfully executed {len(approved)} actions!")
                        
                        # Clear approved actions
                        st.session_state.approved_actions = [
                            a for a in st.session_state.approved_actions 
                            if a["status"] != "approved"
                        ]
                        st.rerun()
                else:
                    st.warning("No approved actions to execute!")
    else:
        st.info("👈 Run analysis in the 'Analysis' tab to get mitigation suggestions!")

with tab4:
    st.markdown("## 📋 Comprehensive Report")
    
    if st.session_state.results is not None:
        results = st.session_state.results
        detection = results['detection']
        early_warning = results['early_warning']
        
        # Generate report
        report_cols = st.columns(3)
        
        with report_cols[0]:
            import json
            report_dict = {
                'config': results['config'],
                'summary': {
                    'n_samples': len(detection['data']),
                    'n_change_points': len(detection['change_points']),
                    'warning_score': early_warning['warning_score'],
                    'is_warning': early_warning['is_warning']
                },
                'change_points': detection['change_points'].tolist(),
                'probabilities': detection['probabilities'].tolist(),
                'data': detection['data'].tolist()
            }
            st.download_button(
                label="📥 Download JSON Report",
                data=json.dumps(report_dict, indent=2),
                file_name=f"regimeshift_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        
        with report_cols[1]:
            st.download_button(
                label="📊 Download CSV Data",
                data=pd.DataFrame({
                    'index': range(len(detection['data'])),
                    'data': detection['data'],
                    'probability': detection['probabilities'],
                    'is_change_point': [i in detection['change_points'] for i in range(len(detection['data']))]
                }).to_csv(index=False),
                file_name=f"regimeshift_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with report_cols[2]:
            if st.button("🖨️ Generate HTML Report", use_container_width=True):
                with st.spinner("Generating report..."):
                    # Simple HTML report
                    html = f"""
                    <html>
                    <head>
                        <title>RegimeShift Sentinel Report</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 40px; }}
                            .header {{ background: #1E3A8A; color: white; padding: 30px; border-radius: 10px; }}
                            .section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                            table {{ width: 100%; border-collapse: collapse; }}
                            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                            th {{ background-color: #1E3A8A; color: white; }}
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <h1>RegimeShift Sentinel Report</h1>
                            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        </div>
                        
                        <div class="section">
                            <h2>Summary</h2>
                            <p>Analyzed {len(detection['data'])} data points</p>
                            <p>Detected {len(detection['change_points'])} change points</p>
                            <p>Warning Score: {early_warning['warning_score']:.2f}</p>
                            <p>Status: {'⚠️ WARNING' if early_warning['is_warning'] else '✅ STABLE'}</p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    st.download_button(
                        label="📄 Download HTML Report",
                        data=html,
                        file_name=f"regimeshift_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html",
                        use_container_width=True
                    )
        
        # Report sections
        st.markdown("### 📊 Executive Summary")
        
        summary_cols = st.columns(2)
        with summary_cols[0]:
            st.markdown("""
            **Key Findings:**
            
            1. **Early Detection**: Bayesian change-point detection provides probabilistic warnings
            2. **Human-in-the-Loop**: All actions require explicit approval
            3. **Safety First**: Only reversible actions are suggested for high-risk systems
            4. **Domain Agnostic**: Works across ML, scientific simulations, and production systems
            """)
        
        with summary_cols[1]:
            st.markdown("""
            **Recommendations:**
            
            ✅ Monitor system for 24 hours after detection  
            ✅ Review logs around change points  
            ✅ Consider implementing suggested mitigations  
            ✅ Adjust thresholds based on false positive rate  
            ⚠️ High warning scores (>0.7) require immediate attention
            """)
        
        # Configuration used
        st.markdown("### ⚙️ Configuration Used")
        config_df = pd.DataFrame([results['config']])
        st.dataframe(config_df, use_container_width=True)
        
        # System insights
        st.markdown("### 🔍 System Insights")
        
        insight_cols = st.columns(3)
        with insight_cols[0]:
            st.info(f"**Detection Method**: Bayesian Online Change-Point Detection")
        
        with insight_cols[1]:
            st.info(f"**Early Warning Signals**: {len(early_warning.get('signals', {}))} indicators monitored")
        
        with insight_cols[2]:
            efficiency = len(detection['change_points']) / len(detection['data']) * 100
            st.info(f"**Detection Efficiency**: {efficiency:.1f}% of series flagged")
        
    else:
        st.info("👈 Run analysis to generate a report!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280;">
    <p>RegimeShift Sentinel v0.1.0 • Radiothon 2026 Submission</p>
    <p>Bayesian early warning system with human-in-the-loop safety</p>
</div>
""", unsafe_allow_html=True)

