"""
CFAR Framework Command Line Interface

# `cfar run --config configs/littering.yml`
"""

import argparse
import yaml
import numpy as np
import json
import csv
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from resolution_engine.state import State
from resolution_engine.dynamics import step
from resolution_engine.estimator import estimate_na_eff, estimate_lambda_eff, estimate_k1, min_resolvable_deltaY
from resolution_engine.controller_pid import PID
from resolution_engine.controller_bandit import ThompsonBandit
from resolution_engine.controller_fluctuation import FluctuationController


def run(path: str, output_file: str = None, output_format: str = "json"):
    """
    Run CFAR Framework simulation with specified configuration
    
    Args:
        path: Path to configuration YAML file
        output_file: Optional output file path for results
        output_format: Output format ('json', 'csv', 'yaml')
    """
    # Load configuration
    cfg = yaml.safe_load(open(path))
    
    # Initialize system state
    s = State(**cfg["init_state"])
    
    # Initialize controllers
    pid = PID(**cfg["pid"])
    bandit = ThompsonBandit(n_arms=len(cfg["fast_arms"]))
    fluctuation = FluctuationController(**cfg.get("fluctuation", {}))
    
    # Get target and simulation parameters
    target = cfg["target_Y"]
    
    print(f"Starting CFAR Framework simulation with target Y = {target}")
    print(f"Initial state: Y={s.Y:.3f}, N={s.N:.3f}, A={s.A:.3f}, C={s.C:.3f}, B={s.B:.3f}")
    print()
    
    # Storage for results
    results = {
        "metadata": {
            "framework": "CFAR Framework",
            "version": "0.1.0",
            "timestamp": datetime.now().isoformat(),
            "config_file": path,
            "target_Y": target,
            "horizon_days": cfg["horizon_days"],
            "initial_state": cfg["init_state"]
        },
        "parameters": {
            "pid": cfg["pid"],
            "fluctuation": cfg.get("fluctuation", {}),
            "fast_arms": cfg["fast_arms"],
            "na_inputs": cfg["na_inputs"],
            "lambda_inputs": cfg["lambda_inputs"],
            "k1_inputs": cfg["k1_inputs"],
            "reward_threshold": cfg["reward_threshold"]
        },
        "simulation_data": []
    }
    
    # Track state history for fluctuation controller
    state_history = [s]
    
    # Run simulation
    for t in range(cfg["horizon_days"]):
        # Estimate system parameters
        na = estimate_na_eff(**cfg["na_inputs"])
        lam = estimate_lambda_eff(**cfg["lambda_inputs"])
        k1 = estimate_k1(**cfg["k1_inputs"])
        dYmin = min_resolvable_deltaY(na, lam, k1)
        
        # Compute control actions with strategy switching
        e = target - s.Y  # error
        
        # Strategy switching based on Rayleigh criterion
        if abs(e) < dYmin:
            # Precision blocked - use fluctuation control
            uC = 0.0  # Freeze structural adjustments
            uF = fluctuation(s, t, state_history)
            control_mode = "fluctuation"
        else:
            # Precision feasible - use PID control
            uC = pid(e, dYmin)  # Structural adjustment
            uF = 0.0
            control_mode = "precision"
        
        # Select message/frame using bandit (always active)
        arm = bandit.select()
        uA = cfg["fast_arms"][arm]["dose"]
        arm_name = cfg["fast_arms"][arm]["name"]
        
        # Step system dynamics
        s = step(s, uA=uA, uC=uC, uF=uF, eps=np.random.normal(0, 0.02))
        state_history.append(s)
        
        # Compute reward for bandit
        reward = float(s.Y > cfg["reward_threshold"])  # toy reward
        bandit.update(arm, reward)
        
        # Store timestep data
        timestep_data = {
            "day": t,
            "state": {
                "Y": float(s.Y),
                "N": float(s.N),
                "A": float(s.A),
                "C": float(s.C),
                "B": float(s.B)
            },
            "parameters": {
                "NA_eff": float(na),
                "lambda_eff": float(lam),
                "k1": float(k1),
                "delta_Y_min": float(dYmin)
            },
            "control": {
                "error": float(e),
                "control_mode": control_mode,
                "uC": float(uC),
                "uA": float(uA),
                "uF": float(uF),
                "selected_arm": int(arm),
                "arm_name": arm_name,
                "reward": float(reward)
            }
        }
        results["simulation_data"].append(timestep_data)
        
        # Print progress with control mode
        mode_indicator = "F" if control_mode == "fluctuation" else "P"
        print(f"day {t:03d}  Y={s.Y:.3f}  N={s.N:.3f}  A={s.A:.3f}  C={s.C:.3f}  B={s.B:.3f}  ΔYmin={dYmin:.3f}  uC={uC:+.3f}  uF={uF:+.3f}  [{mode_indicator}]  arm={arm}({arm_name})")
    
    # Add summary statistics
    final_error = abs(target - s.Y)
    results["summary"] = {
        "final_state": {
            "Y": float(s.Y),
            "N": float(s.N),
            "A": float(s.A),
            "C": float(s.C),
            "B": float(s.B)
        },
        "final_error": float(final_error),
        "target_achieved": bool(final_error < 0.05),  # Within 5% of target
        "days_above_target": sum(1 for day in results["simulation_data"] if day["state"]["Y"] >= target),
        "max_Y_achieved": max(day["state"]["Y"] for day in results["simulation_data"]),
        "arm_usage": {arm["name"]: sum(1 for day in results["simulation_data"] if day["control"]["arm_name"] == arm["name"]) 
                     for arm in cfg["fast_arms"]},
        "control_mode_usage": {
            "precision_days": sum(1 for day in results["simulation_data"] if day["control"]["control_mode"] == "precision"),
            "fluctuation_days": sum(1 for day in results["simulation_data"] if day["control"]["control_mode"] == "fluctuation")
        },
        "total_fluctuation_pulses": sum(1 for day in results["simulation_data"] if day["control"]["uF"] > 0.01)
    }
    
    print()
    print(f"Final state: Y={s.Y:.3f} (target: {target})")
    print(f"Final error: {final_error:.3f}")
    print(f"Days above target: {results['summary']['days_above_target']}/{cfg['horizon_days']}")
    print(f"Max Y achieved: {results['summary']['max_Y_achieved']:.3f}")
    
    # Save results if output file specified
    if output_file:
        save_results(results, output_file, output_format)
        print(f"\nResults saved to: {output_file}")
    
    return results


def save_results(results: Dict[str, Any], output_file: str, output_format: str):
    """
    Save simulation results to file in specified format
    
    Args:
        results: Simulation results dictionary
        output_file: Output file path
        output_format: Format ('json', 'csv', 'yaml')
    """
    output_path = Path(output_file)
    
    if output_format.lower() == 'json':
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    elif output_format.lower() == 'csv':
        # Flatten simulation data for CSV
        csv_data = []
        for day_data in results["simulation_data"]:
            row = {
                'day': day_data['day'],
                'Y': day_data['state']['Y'],
                'N': day_data['state']['N'],
                'A': day_data['state']['A'],
                'C': day_data['state']['C'],
                'B': day_data['state']['B'],
                'NA_eff': day_data['parameters']['NA_eff'],
                'lambda_eff': day_data['parameters']['lambda_eff'],
                'k1': day_data['parameters']['k1'],
                'delta_Y_min': day_data['parameters']['delta_Y_min'],
                'error': day_data['control']['error'],
                'uC': day_data['control']['uC'],
                'uA': day_data['control']['uA'],
                'selected_arm': day_data['control']['selected_arm'],
                'arm_name': day_data['control']['arm_name'],
                'reward': day_data['control']['reward']
            }
            csv_data.append(row)
        
        with open(output_path, 'w', newline='') as f:
            if csv_data:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)
                
        # Also save metadata and summary as separate files
        metadata_path = output_path.with_name(f"{output_path.stem}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump({
                "metadata": results["metadata"],
                "parameters": results["parameters"],
                "summary": results["summary"]
            }, f, indent=2)
    
    elif output_format.lower() == 'yaml':
        with open(output_path, 'w') as f:
            yaml.dump(results, f, default_flow_style=False, indent=2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="CFAR Framework CLI")
    ap.add_argument("command", choices=["run"], help="Command to execute")
    ap.add_argument("--config", required=True, help="Path to configuration YAML file")
    ap.add_argument("--output", "-o", help="Output file path for results")
    ap.add_argument("--format", "-f", choices=["json", "csv", "yaml"], default="json", 
                    help="Output format (default: json)")
    args = ap.parse_args()
    
    if args.command == "run":
        run(args.config, args.output, args.format)
