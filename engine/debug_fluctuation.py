#!/usr/bin/env python3
"""
Debug fluctuation controller behavior
"""

import yaml
from resolution_engine.state import State
from resolution_engine.controller_fluctuation import FluctuationController
from resolution_engine.dynamics import gradient_strength

# Load config
cfg = yaml.safe_load(open("configs/littering.yml"))

# Create test states
early_state = State(Y=0.85, N=0.7, A=0.6, C=0.15, B=0.07)  # Early in simulation
late_state = State(Y=0.98, N=0.95, A=0.9, C=0.05, B=0.06)  # Near peak
decay_state = State(Y=0.85, N=0.85, A=0.95, C=-0.2, B=0.06)  # Constraint decay

# Create controller
fluctuation = FluctuationController(**cfg["fluctuation"])

print("=== Fluctuation Controller Debug ===")
print(f"Config: {cfg['fluctuation']}")
print()

# Test gradient strength calculation
for name, state in [("Early", early_state), ("Peak", late_state), ("Decay", decay_state)]:
    print(f"{name} State: Y={state.Y:.3f}, A={state.A:.3f}, C={state.C:.3f}, B={state.B:.3f}")
    
    # Test different dY_dt values
    for dY_dt in [0.02, 0.005, -0.005]:
        g = gradient_strength(state, dY_dt)
        print(f"  dY/dt={dY_dt:+.3f} -> gradient_strength={g:.3f}")
    
    print()

# Test attention trap detection
print("=== Attention Trap Detection ===")
state_history = [
    State(Y=0.95, N=0.9, A=0.85, C=0.1, B=0.06),
    State(Y=0.95, N=0.9, A=0.87, C=0.08, B=0.06),
    State(Y=0.95, N=0.9, A=0.89, C=0.06, B=0.06),
    State(Y=0.95, N=0.9, A=0.91, C=0.04, B=0.06),
    State(Y=0.95, N=0.9, A=0.93, C=0.02, B=0.06),
    decay_state  # Final state with high A, low C
]

for day in range(len(state_history)):
    if day < 3:
        continue
        
    state = state_history[day]
    uF = fluctuation(state, day, state_history[:day+1])
    
    # Calculate trends manually for debug
    Y_values = [s.Y for s in state_history[max(0, day-5):day+1]]
    C_values = [s.C for s in state_history[max(0, day-5):day+1]]
    
    dY_dt = fluctuation.calculate_slope(Y_values, window=3)
    dC_dt = fluctuation.calculate_slope(C_values, window=3)
    
    trap = fluctuation.detect_attention_trap(state, dY_dt, dC_dt)
    
    print(f"Day {day}: A={state.A:.3f}, C={state.C:.3f}, dY/dt={dY_dt:.3f}, dC/dt={dC_dt:.3f}")
    print(f"  Attention trap: {trap}, uF={uF:.3f}")
    print()
