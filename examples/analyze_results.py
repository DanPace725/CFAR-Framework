#!/usr/bin/env python3
"""
CFAR Framework Results Analysis

Example script showing how to analyze simulation results from different output formats.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse


def load_results(file_path: str):
    """
    Load simulation results from JSON, CSV, or infer from file extension
    
    Args:
        file_path: Path to results file
        
    Returns:
        Dictionary with simulation data or pandas DataFrame for CSV
    """
    path = Path(file_path)
    
    if path.suffix.lower() == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    
    elif path.suffix.lower() == '.csv':
        df = pd.read_csv(path)
        # Try to load metadata if available
        metadata_path = path.with_name(f"{path.stem}_metadata.json")
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        return {"csv_data": df, "metadata": metadata}
    
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")


def analyze_json_results(results: dict):
    """Analyze results from JSON format"""
    print("=== CFAR Framework Simulation Analysis ===")
    print(f"Framework: {results['metadata']['framework']}")
    print(f"Timestamp: {results['metadata']['timestamp']}")
    print(f"Config: {results['metadata']['config_file']}")
    print()
    
    # Summary statistics
    summary = results['summary']
    print("=== Summary Statistics ===")
    print(f"Target Y: {results['metadata']['target_Y']:.3f}")
    print(f"Final Y: {summary['final_state']['Y']:.3f}")
    print(f"Final Error: {summary['final_error']:.3f}")
    print(f"Target Achieved: {summary['target_achieved']}")
    print(f"Days Above Target: {summary['days_above_target']}/{results['metadata']['horizon_days']}")
    print(f"Max Y Achieved: {summary['max_Y_achieved']:.3f}")
    print()
    
    # Arm usage
    print("=== Intervention Arm Usage ===")
    for arm, count in summary['arm_usage'].items():
        percentage = (count / results['metadata']['horizon_days']) * 100
        print(f"{arm}: {count} days ({percentage:.1f}%)")
    print()
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(results['simulation_data'])
    
    # State evolution analysis
    print("=== State Variable Analysis ===")
    state_cols = ['Y', 'N', 'A', 'C', 'B']
    for col in state_cols:
        values = [day['state'][col] for day in results['simulation_data']]
        print(f"{col}: mean={pd.Series(values).mean():.3f}, "
              f"std={pd.Series(values).std():.3f}, "
              f"min={min(values):.3f}, max={max(values):.3f}")
    
    return df


def analyze_csv_results(data: dict):
    """Analyze results from CSV format"""
    df = data['csv_data']
    metadata = data.get('metadata', {})
    
    print("=== CFAR Framework Simulation Analysis (CSV) ===")
    if metadata:
        print(f"Framework: {metadata.get('metadata', {}).get('framework', 'Unknown')}")
        print(f"Target Y: {metadata.get('metadata', {}).get('target_Y', 'Unknown')}")
    print(f"Total Days: {len(df)}")
    print()
    
    # Summary statistics
    print("=== Summary Statistics ===")
    print(f"Final Y: {df['Y'].iloc[-1]:.3f}")
    print(f"Max Y: {df['Y'].max():.3f}")
    print(f"Min Y: {df['Y'].min():.3f}")
    print()
    
    # State variable statistics
    print("=== State Variable Analysis ===")
    state_cols = ['Y', 'N', 'A', 'C', 'B']
    for col in state_cols:
        if col in df.columns:
            print(f"{col}: mean={df[col].mean():.3f}, "
                  f"std={df[col].std():.3f}, "
                  f"min={df[col].min():.3f}, max={df[col].max():.3f}")
    
    return df


def create_plots(df, output_dir="plots"):
    """
    Create visualization plots from simulation data
    
    Args:
        df: DataFrame with simulation data
        output_dir: Directory to save plots
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Set style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # 1. State Evolution Over Time
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('CFAR Framework: State Evolution Over Time', fontsize=16)
    
    state_vars = ['Y', 'N', 'A', 'C', 'B']
    colors = ['blue', 'green', 'orange', 'red', 'purple']
    
    for i, (var, color) in enumerate(zip(state_vars, colors)):
        row = i // 3
        col = i % 3
        
        if var in df.columns:
            axes[row, col].plot(df['day'], df[var], color=color, linewidth=2)
            axes[row, col].set_title(f'{var} (Outcome)' if var == 'Y' else 
                                   f'{var} ({"Norm" if var == "N" else "Attention" if var == "A" else "Constraint" if var == "C" else "Burden"})')
            axes[row, col].set_xlabel('Day')
            axes[row, col].set_ylabel(var)
            axes[row, col].grid(True, alpha=0.3)
    
    # Remove empty subplot
    if len(state_vars) < 6:
        fig.delaxes(axes[1, 2])
    
    plt.tight_layout()
    plt.savefig(output_path / 'state_evolution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Control Actions
    if 'uC' in df.columns and 'uA' in df.columns:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('CFAR Framework: Control Actions', fontsize=16)
        
        ax1.plot(df['day'], df['uC'], color='red', linewidth=2, label='Structural Control (uC)')
        ax1.set_title('PID Controller Output')
        ax1.set_xlabel('Day')
        ax1.set_ylabel('Control Signal')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        ax2.plot(df['day'], df['uA'], color='blue', linewidth=2, label='Attention Control (uA)')
        ax2.set_title('Bandit Controller Output')
        ax2.set_xlabel('Day')
        ax2.set_ylabel('Control Signal')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig(output_path / 'control_actions.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # 3. Resolution Parameters
    if 'delta_Y_min' in df.columns:
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('CFAR Framework: Resolution Parameters', fontsize=16)
        
        params = ['NA_eff', 'lambda_eff', 'k1', 'delta_Y_min']
        param_names = ['Numerical Aperture', 'Wavelength', 'Process Factor', 'Min Resolvable Change']
        
        for i, (param, name) in enumerate(zip(params, param_names)):
            row = i // 2
            col = i % 2
            
            if param in df.columns:
                axes[row, col].plot(df['day'], df[param], linewidth=2)
                axes[row, col].set_title(name)
                axes[row, col].set_xlabel('Day')
                axes[row, col].set_ylabel(param)
                axes[row, col].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / 'resolution_parameters.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # 4. Arm Selection (if available)
    if 'arm_name' in df.columns:
        arm_counts = df['arm_name'].value_counts()
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(arm_counts.index, arm_counts.values)
        plt.title('CFAR Framework: Intervention Arm Usage')
        plt.xlabel('Intervention Type')
        plt.ylabel('Days Used')
        plt.xticks(rotation=45)
        
        # Add percentage labels on bars
        total_days = len(df)
        for bar, count in zip(bars, arm_counts.values):
            percentage = (count / total_days) * 100
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{percentage:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path / 'arm_usage.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"Plots saved to: {output_path.absolute()}")


def main():
    parser = argparse.ArgumentParser(description="Analyze CFAR Framework simulation results")
    parser.add_argument("results_file", help="Path to results file (JSON or CSV)")
    parser.add_argument("--plots", action="store_true", help="Generate visualization plots")
    parser.add_argument("--plot-dir", default="plots", help="Directory for plots (default: plots)")
    
    args = parser.parse_args()
    
    # Load and analyze results
    results = load_results(args.results_file)
    
    if isinstance(results, dict) and 'csv_data' in results:
        # CSV format
        df = analyze_csv_results(results)
    else:
        # JSON format
        df = analyze_json_results(results)
    
    # Generate plots if requested
    if args.plots:
        create_plots(df, args.plot_dir)


if __name__ == "__main__":
    main()
