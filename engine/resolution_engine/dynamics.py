"""
System Dynamics Module

# updates for N,A,C,B; noise; costs
"""

import numpy as np
from typing import Tuple, Dict, Any
from .state import State


def sigma(x): 
    """Sigmoid activation function"""
    return 1/(1+np.exp(-x))


def step(state: State, uA: float, uC: float, uF: float = 0.0, eps=0.0,
         beta=(-0.5, 3.0, 2.0, 2.0, 1.5),  # β0, βN, βA, βC, βB
         eta=0.2, rho=0.9, deltaC=0.02, kappa=0.3):
    """
    Execute one dynamics step
    
    Args:
        state: Current system state
        uA: Attention control input
        uC: Constraint control input
        eps: Random noise
        beta: Model parameters (β0, βN, βA, βC, βB)
        eta: Norm update rate
        rho: Attention decay rate
        deltaC: Constraint decay rate
        kappa: Burden update rate
    
    Returns:
        New system state
    """
    β0, βN, βA, βC, βB = beta
    
    # Calculate gradient strength from fluctuation control
    G = gradient_strength(state) * uF
    
    # Update outcome using sigmoid model with engineered gradients
    Y = sigma(β0 + βN*state.N + βA*state.A + βC*state.C - βB*state.B + G + eps)
    
    # Update norm based on observed outcomes
    N = (1-eta)*state.N + eta*Y
    
    # Update attention with decay and control input
    A = rho*state.A + uA
    
    # Update constraint with control input and natural decay
    C = state.C + uC - deltaC
    
    # Update burden based on intervention costs
    B = (1-kappa)*state.B + kappa*cost(uA, uC, uF)
    
    return State(Y=Y, N=N, A=A, C=C, B=B)


def gradient_strength(state: State, dY_dt: float = 0.0, A_hi: float = 0.8) -> float:
    """
    Calculate gradient strength multiplier for fluctuation control
    
    Args:
        state: Current system state
        dY_dt: Rate of change in Y (outcome slope)
        A_hi: Threshold for high attention
        
    Returns:
        Gradient strength multiplier (0 to ~2)
    """
    # Higher when attention is high (energy available)
    stall = max(0.0, state.A - A_hi) if state.A >= A_hi else 0.0
    
    # Higher when system is stalled (flat outcome trajectory)  
    flat = max(0.0, 0.02 - abs(dY_dt))
    
    # Higher when constraints are weak/decaying (need alternative pathways)
    weakC = max(0.0, 0.5 - max(state.C, 0))  # Increased sensitivity
    
    # Lower when burden is high (avoid backlash)
    guard = max(0.0, 0.8 - state.B)
    
    # Base multiplier to ensure some effect
    base = 0.3
    
    return base + stall * (1 + flat) * (1 + weakC) * guard


def cost(uA: float, uC: float, uF: float = 0.0) -> float:
    """
    Calculate intervention cost
    
    Args:
        uA: Attention intervention magnitude
        uC: Constraint intervention magnitude
        uF: Fluctuation intervention magnitude
        
    Returns:
        Total intervention cost
    """
    return 0.6*abs(uA) + 1.0*abs(uC) + 0.4*abs(uF)


class SystemDynamics:
    """
    System dynamics implementation (class-based interface)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize dynamics with configuration parameters"""
        self.config = config
        
    def step(self, state: State, uA: float, uC: float, eps: float = 0.0) -> State:
        """Execute one dynamics step using class configuration"""
        return step(state, uA, uC, eps, **self.config)
