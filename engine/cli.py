"""
CFAR Framework Command Line Interface

# `cfar run --config configs/littering.yml`
"""

import argparse
import yaml
import numpy as np
from pathlib import Path
from typing import Dict, Any

from resolution_engine.state import State
from resolution_engine.dynamics import step
from resolution_engine.estimator import estimate_na_eff, estimate_lambda_eff, estimate_k1, min_resolvable_deltaY
from resolution_engine.controller_pid import PID
from resolution_engine.controller_bandit import ThompsonBandit


def run(path: str):
    """
    Run resolution system simulation with specified configuration
    
    Args:
        path: Path to configuration YAML file
    """
    # Load configuration
    cfg = yaml.safe_load(open(path))
    
    # Initialize system state
    s = State(**cfg["init_state"])
    
    # Initialize controllers
    pid = PID(**cfg["pid"])
    bandit = ThompsonBandit(n_arms=len(cfg["fast_arms"]))
    
    # Get target and simulation parameters
    target = cfg["target_Y"]
    
    print(f"Starting simulation with target Y = {target}")
    print(f"Initial state: Y={s.Y:.3f}, N={s.N:.3f}, A={s.A:.3f}, C={s.C:.3f}, B={s.B:.3f}")
    print()
    
    # Run simulation
    for t in range(cfg["horizon_days"]):
        # Estimate system parameters
        na = estimate_na_eff(**cfg["na_inputs"])
        lam = estimate_lambda_eff(**cfg["lambda_inputs"])
        k1 = estimate_k1(**cfg["k1_inputs"])
        dYmin = min_resolvable_deltaY(na, lam, k1)
        
        # Compute control actions
        e = target - s.Y  # error
        uC = pid(e, dYmin)  # structural adjustment (PID)
        
        # Select message/frame using bandit
        arm = bandit.select()
        uA = cfg["fast_arms"][arm]["dose"]
        
        # Step system dynamics
        s = step(s, uA=uA, uC=uC, eps=np.random.normal(0, 0.02))
        
        # Compute reward for bandit
        reward = float(s.Y > cfg["reward_threshold"])  # toy reward
        bandit.update(arm, reward)
        
        # Print progress
        arm_name = cfg["fast_arms"][arm]["name"]
        print(f"day {t:03d}  Y={s.Y:.3f}  N={s.N:.3f}  A={s.A:.3f}  C={s.C:.3f}  B={s.B:.3f}  ΔYmin={dYmin:.3f}  uC={uC:+.3f}  arm={arm}({arm_name})")
    
    print()
    print(f"Final state: Y={s.Y:.3f} (target: {target})")
    print(f"Final error: {abs(target - s.Y):.3f}")


if __name__ == "__main__":
    # Simple argument parser for demo
    ap = argparse.ArgumentParser(description="CFAR Framework CLI")
    ap.add_argument("command", choices=["run"], help="Command to execute")
    ap.add_argument("--config", required=True, help="Path to configuration YAML file")
    args = ap.parse_args()
    
    if args.command == "run":
        run(args.config)
