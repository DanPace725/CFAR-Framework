"""
PID Controller Module

# PID with deadband/hysteresis
"""

import numpy as np
from typing import Dict, Any, Optional
from .state import State


class PID:
    """
    PID Controller with deadband and hysteresis
    """
    
    def __init__(self, kp: float, ki: float, kd: float, 
                 deadband: float = 0.005, max_step: float = 0.1, hysteresis: float = 0.01):
        """
        Initialize PID controller
        
        Args:
            kp: Proportional gain
            ki: Integral gain  
            kd: Derivative gain
            deadband: Deadband threshold
            max_step: Maximum step size per iteration
            hysteresis: Hysteresis threshold for direction changes
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.deadband = deadband
        self.max_step = max_step
        self.hysteresis = hysteresis
        
        # Initialize PID state variables
        self.i = 0.0  # integral term
        self.prev_e = 0.0  # previous error
    
    def __call__(self, error: float, deltaY_min: float) -> float:
        """
        Compute PID control output
        
        Args:
            error: Control error (target - measurement)
            deltaY_min: Minimum resolvable change (resolution limit)
            
        Returns:
            Control output
        """
        # Deadband widened by resolution limit
        band = max(self.deadband, deltaY_min)
        if abs(error) < band: 
            return 0.0
            
        # Update integral term
        self.i += error
        
        # Calculate derivative term
        d = error - self.prev_e
        self.prev_e = error
        
        # Compute PID output
        u = self.kp*error + self.ki*self.i + self.kd*d
        
        # Hysteresis: soften direction flips
        if abs(d) > self.hysteresis: 
            u *= 0.7
            
        # Limit step size
        return max(-self.max_step, min(self.max_step, u))
    
    def reset(self):
        """Reset PID controller state"""
        self.i = 0.0
        self.prev_e = 0.0
    
    def set_gains(self, kp: float, ki: float, kd: float):
        """Update PID gains"""
        self.kp = kp
        self.ki = ki
        self.kd = kd


# Alias for backward compatibility
PIDController = PID
