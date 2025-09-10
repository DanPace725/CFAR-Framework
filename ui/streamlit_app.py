"""
Streamlit Application for CFAR Framework

Interactive dashboard for Constraint-Fluctuation-Attention-Resolution system monitoring and control
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
import yaml
from pathlib import Path
import subprocess
import tempfile
import os
from datetime import datetime
import io

# Import resolution engine components
import sys
sys.path.append(str(Path(__file__).parent.parent / "engine"))
from resolution_engine.state import State
from resolution_engine.dynamics import step
from resolution_engine.controller_fluctuation import FluctuationController


def main():
    """
    Main Streamlit application
    """
    st.set_page_config(
        page_title="CFAR Framework",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 CFAR Framework")
    st.markdown("*Interactive dashboard for Constraint-Fluctuation-Attention-Resolution system monitoring and control*")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "System Configuration", "Performance Analytics", "Documentation"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "System Configuration":
        show_configuration()
    elif page == "Performance Analytics":
        show_analytics()
    elif page == "Documentation":
        show_documentation()


def show_dashboard():
    """
    Main dashboard view with real-time simulation capabilities
    """
    st.header("🎯 CFAR Framework Dashboard")
    
    # File upload section
    st.subheader("📁 Load Simulation Results")
    uploaded_file = st.file_uploader("Choose a simulation results file", type=['json'])
    
    if uploaded_file is not None:
        # Load and display results
        results = json.load(uploaded_file)
        display_simulation_results(results)
    else:
        st.info("Upload a simulation results JSON file to view dashboard")
        
        # Show example run button
        if st.button("🚀 Run Example Simulation"):
            run_example_simulation()


def display_simulation_results(results):
    """Display comprehensive dashboard for simulation results"""
    
    # Extract key metrics
    metadata = results['metadata']
    summary = results['summary']
    simulation_data = results['simulation_data']
    
    # Header metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Target Y", f"{metadata['target_Y']:.3f}")
    with col2:
        final_y = summary['final_state']['Y']
        delta = final_y - metadata['target_Y']
        st.metric("Final Y", f"{final_y:.3f}", f"{delta:+.3f}")
    with col3:
        st.metric("Days Above Target", f"{summary['days_above_target']}/{metadata['horizon_days']}")
    with col4:
        achieved = "✅" if summary['target_achieved'] else "❌"
        st.metric("Target Achieved", achieved)
    
    # Control mode analysis (new feature)
    if 'control_mode_usage' in summary:
        st.subheader("🔄 Control Mode Analysis")
        col1, col2, col3 = st.columns(3)
        
        precision_days = summary['control_mode_usage']['precision_days']
        fluctuation_days = summary['control_mode_usage']['fluctuation_days']
        total_days = metadata['horizon_days']
        
        with col1:
            st.metric("Precision Mode [P]", f"{precision_days} days", f"{precision_days/total_days*100:.1f}%")
        with col2:
            st.metric("Fluctuation Mode [F]", f"{fluctuation_days} days", f"{fluctuation_days/total_days*100:.1f}%")
        with col3:
            st.metric("Fluctuation Pulses", summary.get('total_fluctuation_pulses', 0))
    
    # Convert to DataFrame for plotting
    df = pd.DataFrame(simulation_data)
    
    # Debug info
    st.write(f"**Debug**: DataFrame shape: {df.shape}")
    if not df.empty:
        st.write(f"**Debug**: Columns: {list(df.columns)}")
        st.write(f"**Debug**: First row keys: {list(df.iloc[0].keys()) if len(df) > 0 else 'No data'}")
    
    # State evolution plot
    st.subheader("📊 State Evolution Over Time")
    fig = create_state_evolution_plot(df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Control actions plot
    st.subheader("🎛️ Control Actions")
    fig = create_control_actions_plot(df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Control mode timeline (new)
    if 'control_mode' in df.columns:
        st.subheader("⏱️ Control Mode Timeline")
        fig = create_control_timeline_plot(df)
        st.plotly_chart(fig, use_container_width=True)
    
    # Arm usage
    st.subheader("🎯 Intervention Strategy Usage")
    fig = create_arm_usage_plot(summary['arm_usage'])
    st.plotly_chart(fig, use_container_width=True)
    
    # Export and interpretation section
    st.subheader("📄 Export & Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Generate Detailed Report"):
            generate_detailed_report(results)
    
    with col2:
        if st.button("💾 Download CSV Data"):
            csv_data = export_csv_data(results)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"cfar_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📋 Copy Summary"):
            summary_text = generate_summary_text(results)
            st.text_area("Summary (copy this):", summary_text, height=200)


def create_state_evolution_plot(df):
    """Create interactive state evolution plot"""
    fig = go.Figure()
    
    state_vars = ['Y', 'N', 'A', 'C', 'B']
    colors = ['blue', 'green', 'orange', 'red', 'purple']
    
    for var, color in zip(state_vars, colors):
        # Extract state values from nested structure
        values = []
        days = []
        for _, row in df.iterrows():
            if 'state' in row and isinstance(row['state'], dict) and var in row['state']:
                values.append(row['state'][var])
                days.append(row['day'])
        
        if values:  # Only add trace if we have data
            fig.add_trace(go.Scatter(
                x=days,
                y=values,
                mode='lines',
                name=var,
                line=dict(color=color, width=2)
            ))
    
    fig.update_layout(
        title="CFAR Framework: State Variables Over Time",
        xaxis_title="Day",
        yaxis_title="Value",
        hovermode='x unified'
    )
    
    return fig


def create_control_actions_plot(df):
    """Create control actions plot with fluctuation highlighting"""
    fig = go.Figure()
    
    # Extract control data from nested structure
    days = []
    uC_values = []
    uA_values = []
    uF_values = []
    pulse_days = []
    pulse_values = []
    
    for _, row in df.iterrows():
        if 'control' in row and isinstance(row['control'], dict):
            days.append(row['day'])
            uC_values.append(row['control'].get('uC', 0))
            uA_values.append(row['control'].get('uA', 0))
            uF_val = row['control'].get('uF', 0)
            uF_values.append(uF_val)
            
            # Track fluctuation pulses
            if uF_val > 0.01:
                pulse_days.append(row['day'])
                pulse_values.append(uF_val)
    
    # Add traces if we have data
    if days:
        # PID Control
        fig.add_trace(go.Scatter(
            x=days,
            y=uC_values,
            mode='lines',
            name='Structural Control (uC)',
            line=dict(color='red', width=2)
        ))
        
        # Attention Control
        fig.add_trace(go.Scatter(
            x=days,
            y=uA_values,
            mode='lines',
            name='Attention Control (uA)',
            line=dict(color='blue', width=2)
        ))
        
        # Fluctuation Control
        fig.add_trace(go.Scatter(
            x=days,
            y=uF_values,
            mode='lines',
            name='Fluctuation Control (uF)',
            line=dict(color='purple', width=2)
        ))
        
        # Highlight fluctuation pulses
        if pulse_days:
            fig.add_trace(go.Scatter(
                x=pulse_days,
                y=pulse_values,
                mode='markers',
                name='Fluctuation Pulses',
                marker=dict(color='orange', size=8)
            ))
    
    fig.update_layout(
        title="CFAR Framework: Control Actions Over Time",
        xaxis_title="Day",
        yaxis_title="Control Signal",
        hovermode='x unified'
    )
    
    return fig


def create_control_timeline_plot(df):
    """Create control mode timeline visualization"""
    fig = go.Figure()
    
    # Extract control mode data from nested structure
    days = []
    precision_y = []
    fluctuation_y = []
    pulse_days = []
    
    for _, row in df.iterrows():
        if 'control' in row and isinstance(row['control'], dict):
            days.append(row['day'])
            control_mode = row['control'].get('control_mode', 'fluctuation')
            
            if control_mode == 'precision':
                precision_y.append(1)
                fluctuation_y.append(0)
            else:
                precision_y.append(0)
                fluctuation_y.append(1)
            
            # Track fluctuation pulses
            if row['control'].get('uF', 0) > 0.01:
                pulse_days.append(row['day'])
    
    if days:  # Only create plot if we have data
        fig.add_trace(go.Scatter(
            x=days,
            y=precision_y,
            mode='lines',
            fill='tozeroy',
            name='Precision Mode [P]',
            line=dict(color='blue'),
            fillcolor='rgba(0,0,255,0.3)'
        ))
        
        fig.add_trace(go.Scatter(
            x=days,
            y=fluctuation_y,
            mode='lines',
            fill='tozeroy',
            name='Fluctuation Mode [F]',
            line=dict(color='purple'),
            fillcolor='rgba(128,0,128,0.3)'
        ))
        
        # Mark fluctuation pulses
        if pulse_days:
            for day in pulse_days:
                fig.add_vline(x=day, line=dict(color='orange', dash='dash'), opacity=0.7)
    
    fig.update_layout(
        title="Control Mode Timeline (Orange lines = Fluctuation Pulses)",
        xaxis_title="Day",
        yaxis_title="Mode Active",
        yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['Inactive', 'Active']),
        hovermode='x unified'
    )
    
    return fig


def create_arm_usage_plot(arm_usage):
    """Create intervention arm usage plot"""
    arms = list(arm_usage.keys())
    counts = list(arm_usage.values())
    
    fig = go.Figure(data=[go.Bar(x=arms, y=counts, marker_color='skyblue')])
    fig.update_layout(
        title="Intervention Strategy Usage",
        xaxis_title="Strategy Type",
        yaxis_title="Days Used"
    )
    
    return fig


def run_example_simulation():
    """Run example simulation and display results"""
    with st.spinner("Running CFAR Framework simulation..."):
        try:
            temp_output_path = Path("temp_simulation.json")
            
            # Run CLI simulation with proper encoding handling
            result = subprocess.run([
                "python", "engine/cli.py", "run",
                "--config", "engine/configs/littering.yml",
                "--output", str(temp_output_path)
            ], capture_output=True, text=True, cwd=Path.cwd(),
               encoding='utf-8', errors='replace')
            
            if result.returncode == 0:
                # Load and display results
                with open(temp_output_path, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                display_simulation_results(results)
                
                # Clean up
                if temp_output_path.exists():
                    temp_output_path.unlink()
                st.success("✅ Simulation completed successfully!")
            else:
                st.error("❌ Simulation failed!")
                if result.stderr:
                    st.error(f"**Error details:**\n```\n{result.stderr}\n```")
                if result.stdout:
                    st.info(f"**Output:**\n```\n{result.stdout}\n```")
                
        except Exception as e:
            st.error(f"❌ Error running simulation: {str(e)}")
            import traceback
            st.error(f"**Traceback:**\n```\n{traceback.format_exc()}\n```")


def show_configuration():
    """
    System configuration interface for editing simulation parameters
    """
    st.header("⚙️ System Configuration")
    
    # Load default config
    config_path = Path("engine/configs/littering.yml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        st.subheader("📋 Current Configuration")
        
        # Basic parameters
        col1, col2 = st.columns(2)
        with col1:
            target_Y = st.slider("Target Y", 0.0, 1.0, config['target_Y'], 0.01)
            horizon_days = st.number_input("Simulation Days", 1, 365, config['horizon_days'])
        
        with col2:
            reward_threshold = st.slider("Reward Threshold", 0.0, 1.0, config['reward_threshold'], 0.01)
        
        # Initial state
        st.subheader("🎯 Initial System State")
        col1, col2, col3 = st.columns(3)
        with col1:
            init_Y = st.slider("Initial Y", 0.0, 1.0, config['init_state']['Y'], 0.01)
            init_N = st.slider("Initial N", 0.0, 1.0, config['init_state']['N'], 0.01)
        with col2:
            init_A = st.slider("Initial A", 0.0, 1.0, config['init_state']['A'], 0.01)
            init_C = st.slider("Initial C", 0.0, 1.0, config['init_state']['C'], 0.01)
        with col3:
            init_B = st.slider("Initial B", 0.0, 1.0, config['init_state']['B'], 0.01)
        
        # PID parameters
        st.subheader("🎛️ PID Controller")
        col1, col2, col3 = st.columns(3)
        with col1:
            kp = st.slider("Proportional Gain", 0.0, 2.0, config['pid']['kp'], 0.1)
            ki = st.slider("Integral Gain", 0.0, 1.0, config['pid']['ki'], 0.1)
        with col2:
            kd = st.slider("Derivative Gain", 0.0, 1.0, config['pid']['kd'], 0.1)
            deadband = st.slider("Deadband", 0.0, 0.1, config['pid']['deadband'], 0.001)
        with col3:
            max_step = st.slider("Max Step", 0.0, 0.2, config['pid']['max_step'], 0.01)
            hysteresis = st.slider("Hysteresis", 0.0, 0.1, config['pid']['hysteresis'], 0.001)
        
        # Fluctuation controller
        st.subheader("🌊 Fluctuation Controller")
        col1, col2 = st.columns(2)
        with col1:
            max_uF = st.slider("Max uF", 0.0, 0.5, config['fluctuation']['max_uF'], 0.01)
            cooldown_days = st.number_input("Cooldown Days", 1, 30, config['fluctuation']['cooldown_days'])
        with col2:
            A_threshold = st.slider("Attention Threshold", 0.0, 1.0, config['fluctuation']['A_threshold'], 0.01)
            stall_threshold = st.slider("Stall Threshold", 0.0, 0.1, config['fluctuation']['stall_threshold'], 0.001)
        
        # Create modified config
        modified_config = config.copy()
        modified_config.update({
            'target_Y': target_Y,
            'horizon_days': horizon_days,
            'reward_threshold': reward_threshold,
            'init_state': {
                'Y': init_Y, 'N': init_N, 'A': init_A, 'C': init_C, 'B': init_B
            },
            'pid': {
                'kp': kp, 'ki': ki, 'kd': kd,
                'deadband': deadband, 'max_step': max_step, 'hysteresis': hysteresis
            },
            'fluctuation': {
                'max_uF': max_uF, 'cooldown_days': cooldown_days,
                'A_threshold': A_threshold, 'stall_threshold': stall_threshold
            }
        })
        
        # Run simulation button
        if st.button("🚀 Run Simulation with Custom Config"):
            run_custom_simulation(modified_config)
    else:
        st.error("❌ Configuration file not found")


def show_analytics():
    """
    Performance analytics view for comparing simulation runs
    """
    st.header("📈 Performance Analytics")
    
    # File upload for multiple simulations
    st.subheader("📁 Compare Simulation Runs")
    uploaded_files = st.file_uploader(
        "Upload multiple simulation results for comparison", 
        type=['json'], 
        accept_multiple_files=True
    )
    
    if uploaded_files and len(uploaded_files) > 1:
        # Load all results
        all_results = []
        for file in uploaded_files:
            results = json.load(file)
            results['filename'] = file.name
            all_results.append(results)
        
        # Comparison metrics
        st.subheader("📊 Comparison Metrics")
        
        comparison_data = []
        for results in all_results:
            comparison_data.append({
                'File': results['filename'],
                'Target Y': results['metadata']['target_Y'],
                'Final Y': results['summary']['final_state']['Y'],
                'Final Error': results['summary']['final_error'],
                'Target Achieved': results['summary']['target_achieved'],
                'Max Y': results['summary']['max_Y_achieved'],
                'Days Above Target': results['summary']['days_above_target'],
                'Precision Days': results['summary'].get('control_mode_usage', {}).get('precision_days', 0),
                'Fluctuation Days': results['summary'].get('control_mode_usage', {}).get('fluctuation_days', 0),
                'Fluctuation Pulses': results['summary'].get('total_fluctuation_pulses', 0)
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison)
        
        # Comparative plots
        st.subheader("📈 Comparative Analysis")
        
        # Performance comparison
        fig = go.Figure()
        for i, results in enumerate(all_results):
            sim_data = pd.DataFrame(results['simulation_data'])
            y_values = [day['state']['Y'] for day in sim_data.to_dict('records')]
            
            fig.add_trace(go.Scatter(
                x=sim_data['day'],
                y=y_values,
                mode='lines',
                name=results['filename'],
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title="Performance Comparison: Y Over Time",
            xaxis_title="Day",
            yaxis_title="Y Value",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif uploaded_files and len(uploaded_files) == 1:
        st.info("Upload at least 2 files for comparison analysis")
    else:
        st.info("Upload simulation result files to compare performance")


def run_custom_simulation(config):
    """Run simulation with custom configuration"""
    with st.spinner("Running custom simulation..."):
        try:
            # Save temporary config
            temp_config_path = Path("temp_config.yml")
            temp_output_path = Path("temp_custom_simulation.json")
            
            with open(temp_config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            # Run simulation with proper encoding handling
            result = subprocess.run([
                "python", "engine/cli.py", "run",
                "--config", str(temp_config_path),
                "--output", str(temp_output_path)
            ], capture_output=True, text=True, cwd=Path.cwd(), 
               encoding='utf-8', errors='replace')
            
            if result.returncode == 0:
                # Load and display results
                with open(temp_output_path, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                
                st.success("✅ Custom simulation completed!")
                display_simulation_results(results)
                
                # Cleanup
                if temp_config_path.exists():
                    temp_config_path.unlink()
                if temp_output_path.exists():
                    temp_output_path.unlink()
            else:
                st.error("❌ Simulation failed!")
                if result.stderr:
                    st.error(f"**Error details:**\n```\n{result.stderr}\n```")
                if result.stdout:
                    st.info(f"**Output:**\n```\n{result.stdout}\n```")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            st.error(f"**Traceback:**\n```\n{traceback.format_exc()}\n```")


def show_documentation():
    """
    Documentation viewer
    """
    st.header("📚 Documentation")
    
    st.markdown("""
    ## CFAR Framework Documentation
    
    ### Core Concepts
    - **C** (Constraint): System structure and institutional inertia
    - **F** (Fluctuation): Designed variance and gradient engineering  
    - **A** (Attention): Energy flow and cognitive resources
    - **R** (Resolution): Rayleigh-limited precision boundaries
    
    ### Control Modes
    - **Precision Mode [P]**: Fine structural adjustments via PID when resolution allows
    - **Fluctuation Mode [F]**: Gradient engineering when precision is blocked
    
    ### Key Features
    - **Bimodal Control**: Automatic switching between precision and fluctuation strategies
    - **Attention Trap Detection**: Identifies high A + flat dY/dt + declining C scenarios
    - **Resolution-Aware**: Respects physical limits while providing alternative pathways
    
    ### Getting Started
    1. Upload simulation results to the Dashboard
    2. Experiment with parameters in System Configuration
    3. Compare different runs in Performance Analytics
    
    ### Theory Background
    Based on Attention-Fluctuation Dynamics (AFD) and Constraint-Fluctuation-Attention (CFA) models.
    See `/theory/` directory for detailed mathematical foundations.
    """)
    
    st.subheader("🔗 Available Resources")
    st.markdown("""
    - [Theory Documentation](/docs/theory/)
    - [API Reference](/docs/api/)
    - [Examples](/examples/)
    - [Whitepaper](/docs/whitepaper.md)
    - [GitHub Repository](https://github.com/TODO/cfar-framework)
    """)


def generate_detailed_report(results):
    """Generate and display detailed interpretive report"""
    
    # Quick analysis
    metadata = results['metadata']
    summary = results['summary']
    
    st.subheader("🔍 Interpretive Analysis")
    
    # Performance analysis
    final_Y = summary['final_state']['Y']
    target_Y = metadata['target_Y']
    performance_ratio = final_Y / target_Y
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Performance Ratio", f"{performance_ratio:.1%}", 
                 f"{(final_Y - target_Y)*100:+.1f}pp vs target")
        
        # Performance grade
        if performance_ratio >= 0.95:
            grade = "A"
            grade_color = "🟢"
        elif performance_ratio >= 0.85:
            grade = "B" 
            grade_color = "🟡"
        elif performance_ratio >= 0.75:
            grade = "C"
            grade_color = "🟠"
        else:
            grade = "D"
            grade_color = "🔴"
        
        st.metric("Performance Grade", f"{grade_color} {grade}")
    
    with col2:
        # Control strategy analysis
        if 'control_mode_usage' in summary:
            precision_pct = summary['control_mode_usage']['precision_days'] / metadata['horizon_days'] * 100
            fluctuation_pct = summary['control_mode_usage']['fluctuation_days'] / metadata['horizon_days'] * 100
            
            st.metric("Control Strategy", 
                     "Precision-Capable" if precision_pct > 50 else "Fluctuation-Reliant",
                     f"{precision_pct:.0f}% precision mode")
            
            pulse_count = summary.get('total_fluctuation_pulses', 0)
            pulse_frequency = pulse_count / metadata['horizon_days'] * 100
            st.metric("Gradient Engineering", f"{pulse_count} pulses", 
                     f"{pulse_frequency:.1f} per 100 days")
    
    # Key insights
    st.subheader("💡 Key Insights")
    
    insights = []
    
    # Performance insights
    if performance_ratio >= 0.95:
        insights.append("🎯 **Target Achievement**: System successfully reached target performance.")
    else:
        gap = target_Y - final_Y
        insights.append(f"⚠️ **Performance Gap**: System fell short of target by {gap:.1%}.")
    
    # Control insights
    if 'control_mode_usage' in summary:
        if fluctuation_pct > 80:
            insights.append(f"🌊 **Resolution-Limited**: System operated in fluctuation mode {fluctuation_pct:.0f}% of the time, indicating frequent resolution limits.")
        elif precision_pct > 60:
            insights.append(f"🎛️ **Precision-Capable**: System maintained precision mode {precision_pct:.0f}% of the time.")
    
    # Fluctuation insights
    if pulse_count > 10:
        insights.append(f"⚡ **Active Gradient Engineering**: {pulse_count} fluctuation pulses created alternative pathways when precision was blocked.")
    elif pulse_count < 3:
        insights.append("🔄 **Minimal Fluctuation**: Few gradient engineering interventions suggests either good precision or insufficient fluctuation sensitivity.")
    
    # Display insights
    for insight in insights:
        st.info(insight)
    
    # Recommendations
    st.subheader("🎯 Recommendations")
    
    recommendations = []
    
    if performance_ratio < 0.9:
        if pulse_count < 5:
            recommendations.append("⚡ **Increase Fluctuation Control**: Consider lowering attention threshold or reducing cooldown to enable more gradient engineering.")
        else:
            recommendations.append("🎯 **Adjust Target**: Current target may be beyond system capacity given constraints.")
    
    if fluctuation_pct > 80:
        recommendations.append("🔧 **Improve Resolution**: Consider increasing sensing features, reducing intervention cadence, or improving operational precision.")
    
    if pulse_count > 20:
        recommendations.append("💡 **Attention Management**: High fluctuation activity suggests potential attention allocation optimization opportunities.")
    
    # Display recommendations
    for rec in recommendations:
        st.success(rec)


def export_csv_data(results):
    """Export simulation data as CSV"""
    
    # Flatten nested data structure
    flattened_data = []
    
    for day_data in results['simulation_data']:
        row = {'day': day_data['day']}
        
        # Add state variables
        for var in ['Y', 'N', 'A', 'C', 'B']:
            row[f'state_{var}'] = day_data['state'][var]
        
        # Add control variables  
        for var in ['uC', 'uA', 'uF', 'control_mode', 'arm_name']:
            row[f'control_{var}'] = day_data['control'][var]
        
        # Add parameters
        for var in ['NA_eff', 'lambda_eff', 'k1', 'delta_Y_min']:
            row[f'param_{var}'] = day_data['parameters'][var]
        
        flattened_data.append(row)
    
    # Create CSV
    df = pd.DataFrame(flattened_data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    return csv_buffer.getvalue()


def generate_summary_text(results):
    """Generate a text summary for copying/sharing"""
    
    metadata = results['metadata']
    summary = results['summary']
    
    summary_text = f"""
CFAR Framework Simulation Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CONFIGURATION:
• Target Performance: {metadata['target_Y']:.1%}
• Simulation Period: {metadata['horizon_days']} days
• Initial State: Y={metadata['initial_state']['Y']:.1%}

RESULTS:
• Final Performance: {summary['final_state']['Y']:.1%}
• Peak Performance: {summary['max_Y_achieved']:.1%}
• Target Achieved: {'Yes' if summary['target_achieved'] else 'No'}
• Days Above Target: {summary['days_above_target']}/{metadata['horizon_days']}

CONTROL STRATEGY:"""
    
    if 'control_mode_usage' in summary:
        precision_days = summary['control_mode_usage']['precision_days']
        fluctuation_days = summary['control_mode_usage']['fluctuation_days']
        total_days = metadata['horizon_days']
        
        summary_text += f"""
• Precision Mode: {precision_days} days ({precision_days/total_days*100:.1f}%)
• Fluctuation Mode: {fluctuation_days} days ({fluctuation_days/total_days*100:.1f}%)
• Fluctuation Pulses: {summary.get('total_fluctuation_pulses', 0)}"""
    
    summary_text += f"""

INTERVENTION USAGE:"""
    
    for arm, count in summary['arm_usage'].items():
        percentage = (count / metadata['horizon_days']) * 100
        summary_text += f"""
• {arm.title()}: {count} days ({percentage:.1f}%)"""
    
    # Performance assessment
    performance_ratio = summary['final_state']['Y'] / metadata['target_Y']
    if performance_ratio >= 0.95:
        assessment = "Excellent - Target achieved"
    elif performance_ratio >= 0.85:
        assessment = "Good - Near target performance"  
    elif performance_ratio >= 0.75:
        assessment = "Fair - Moderate performance"
    else:
        assessment = "Poor - Below target performance"
    
    summary_text += f"""

OVERALL ASSESSMENT: {assessment}

Generated by CFAR Framework Dashboard
"""
    
    return summary_text


if __name__ == "__main__":
    main()