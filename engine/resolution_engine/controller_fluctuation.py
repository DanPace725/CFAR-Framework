"""
Fluctuation Controller Module

# Engineered gradient creation for attention flow when precision is blocked
"""

import numpy as np
from typing import Dict, Any, List, Optional
from .state import State
from .dynamics import gradient_strength


class FluctuationController:
    """
    Fluctuation controller for creating engineered gradients when PID precision is blocked
    
    This controller activates when the Rayleigh criterion prevents fine structural adjustments,
    providing alternative pathways for attention to create beneficial change through designed
    variance and micro-disruptions.
    """
    
    def __init__(self, max_uF: float = 0.2, cooldown_days: int = 7, 
                 A_threshold: float = 0.8, stall_threshold: float = 0.01):
        """
        Initialize fluctuation controller
        
        Args:
            max_uF: Maximum fluctuation control magnitude
            cooldown_days: Minimum days between fluctuation pulses
            A_threshold: Attention level that triggers fluctuation consideration
            stall_threshold: dY/dt threshold for detecting stalled progress
        """
        self.max_uF = max_uF
        self.cooldown_days = cooldown_days
        self.A_threshold = A_threshold
        self.stall_threshold = stall_threshold
        
        # State tracking
        self.last_fire_day = -999
        self.history = []
        
    def detect_attention_trap(self, state: State, dY_dt: float, C_trend: float) -> bool:
        """
        Detect attention trap: high A + flat dY/dt + declining C
        
        Args:
            state: Current system state
            dY_dt: Rate of change in outcome
            C_trend: Trend in constraint values (negative = declining)
            
        Returns:
            True if attention trap detected
        """
        high_attention = state.A > self.A_threshold
        stalled_progress = abs(dY_dt) < self.stall_threshold
        declining_structure = C_trend < -0.01 or state.C < 0.1  # Constraint decay or very low
        
        return high_attention and stalled_progress and declining_structure
    
    def calculate_slope(self, values: List[float], window: int = 7) -> float:
        """Calculate slope of recent values using linear regression"""
        if len(values) < 2:
            return 0.0
            
        recent = values[-min(window, len(values)):]
        if len(recent) < 2:
            return 0.0
            
        x = np.arange(len(recent))
        y = np.array(recent)
        
        # Simple linear regression
        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]
            return slope
        return 0.0
    
    def __call__(self, state: State, day: int, state_history: List[State]) -> float:
        """
        Compute fluctuation control output
        
        Args:
            state: Current system state
            day: Current simulation day
            state_history: History of system states
            
        Returns:
            Fluctuation control signal uF
        """
        # Check cooldown
        if day - self.last_fire_day < self.cooldown_days:
            return 0.0
            
        # Calculate recent trends
        if len(state_history) < 3:
            return 0.0
            
        Y_values = [s.Y for s in state_history[-10:]]  # Last 10 days
        C_values = [s.C for s in state_history[-10:]]
        
        dY_dt = self.calculate_slope(Y_values, window=5)
        dC_dt = self.calculate_slope(C_values, window=5)
        
        # Check for attention trap
        attention_trap = self.detect_attention_trap(state, dY_dt, dC_dt)
        
        if not attention_trap:
            return 0.0
            
        # Calculate gradient strength potential
        g = gradient_strength(state, dY_dt)
        
        # Scale by available headroom and system capacity
        attention_headroom = min(1.0, state.A / self.A_threshold)
        burden_guard = max(0.0, 0.8 - state.B)  # Reduce if burden high
        
        uF = min(self.max_uF, 0.5 * g * attention_headroom * burden_guard)
        
        # Only fire if significant potential (lowered threshold)
        if uF > 0.02:
            self.last_fire_day = day
            return uF
            
        return 0.0
    
    def get_status(self, day: int) -> Dict[str, Any]:
        """Get controller status information"""
        return {
            "last_fire_day": self.last_fire_day,
            "days_since_fire": day - self.last_fire_day,
            "cooldown_remaining": max(0, self.cooldown_days - (day - self.last_fire_day)),
            "ready_to_fire": (day - self.last_fire_day) >= self.cooldown_days
        }


class AdaptiveFluctuationController(FluctuationController):
    """
    Enhanced fluctuation controller with adaptive parameters based on system learning
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.effectiveness_history = []
        self.adaptation_rate = 0.1
        
    def update_effectiveness(self, pre_state: State, post_states: List[State], days_after: int = 5):
        """
        Update controller effectiveness based on outcomes after fluctuation pulse
        
        Args:
            pre_state: State before fluctuation pulse
            post_states: States following the pulse
            days_after: Number of days to evaluate impact
        """
        if len(post_states) < days_after:
            return
            
        # Measure improvement in outcome trajectory
        pre_Y = pre_state.Y
        post_Y_trend = self.calculate_slope([s.Y for s in post_states[:days_after]])
        
        # Positive effectiveness if trend improved
        effectiveness = post_Y_trend if post_Y_trend > 0 else -0.1
        
        self.effectiveness_history.append(effectiveness)
        
        # Adapt parameters based on recent effectiveness
        if len(self.effectiveness_history) >= 3:
            recent_effectiveness = np.mean(self.effectiveness_history[-3:])
            
            if recent_effectiveness > 0.01:  # Effective
                self.max_uF = min(0.3, self.max_uF * (1 + self.adaptation_rate))
                self.cooldown_days = max(3, int(self.cooldown_days * 0.9))
            elif recent_effectiveness < -0.005:  # Counterproductive
                self.max_uF = max(0.05, self.max_uF * (1 - self.adaptation_rate))
                self.cooldown_days = min(14, int(self.cooldown_days * 1.1))


def create_fluctuation_strategies() -> Dict[str, Dict[str, Any]]:
    """
    Define catalog of fluctuation strategies for different contexts
    
    Returns:
        Dictionary of strategy configurations
    """
    return {
        "novelty_rotation": {
            "description": "Rotate frames, visuals, and messaging approaches",
            "max_uF": 0.15,
            "cooldown": 5,
            "contexts": ["high_habituation", "attention_saturation"]
        },
        
        "temporal_jitter": {
            "description": "Introduce micro-cadence changes and timing variations", 
            "max_uF": 0.10,
            "cooldown": 3,
            "contexts": ["routine_staleness", "predictability_trap"]
        },
        
        "context_refocusing": {
            "description": "Pair with fresh local stats or new anchor points",
            "max_uF": 0.20,
            "cooldown": 7,
            "contexts": ["norm_saturation", "reference_drift"]
        },
        
        "micro_environment": {
            "description": "Small physical environment or affordance tweaks",
            "max_uF": 0.25,
            "cooldown": 10,
            "contexts": ["structural_decay", "constraint_erosion"]
        },
        
        "attention_pulse": {
            "description": "Coordinated A→C→A pulses for system reset",
            "max_uF": 0.30,
            "cooldown": 14,
            "contexts": ["system_reset", "phase_transition"]
        }
    }
