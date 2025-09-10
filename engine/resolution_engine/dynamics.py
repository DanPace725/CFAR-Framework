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


def step(state: State, uA: float, uC: float, eps=0.0,
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
    
    # Update outcome using sigmoid model
    Y = sigma(β0 + βN*state.N + βA*state.A + βC*state.C - βB*state.B + eps)
    
    # Update norm based on observed outcomes
    N = (1-eta)*state.N + eta*Y
    
    # Update attention with decay and control input
    A = rho*state.A + uA
    
    # Update constraint with control input and natural decay
    C = state.C + uC - deltaC
    
    # Update burden based on intervention costs
    B = (1-kappa)*state.B + kappa*cost(uA, uC)
    
    return State(Y=Y, N=N, A=A, C=C, B=B)


def cost(uA: float, uC: float) -> float:
    """
    Calculate intervention cost
    
    Args:
        uA: Attention intervention magnitude
        uC: Constraint intervention magnitude
        
    Returns:
        Total intervention cost
    """
    return 0.6*abs(uA) + 1.0*abs(uC)


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
