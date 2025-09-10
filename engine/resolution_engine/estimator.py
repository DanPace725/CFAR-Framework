"""
Parameter Estimation Module

# estimate NA_eff, λ_eff, k1 from logs
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from .state import State


def estimate_na_eff(sensing_features: int, actuation_channels: int, feedback_latency_days: float) -> float:
    """
    Estimate effective numerical aperture
    
    Args:
        sensing_features: Number of sensing features/dimensions
        actuation_channels: Number of actuation channels
        feedback_latency_days: Feedback latency in days
        
    Returns:
        Effective numerical aperture (0 to 1)
    """
    # Simple monotone proxy in [0,1]
    s = np.tanh(0.15*sensing_features)
    a = np.tanh(0.25*actuation_channels)
    l = 1.0 / (1.0 + 0.1*feedback_latency_days)
    return np.clip(0.5*(s+a)*l, 0, 1)


def estimate_lambda_eff(cadence_days: float, spatial_scale_km: float) -> float:
    """
    Estimate effective wavelength
    
    Args:
        cadence_days: Intervention cadence in days
        spatial_scale_km: Spatial scale in kilometers
        
    Returns:
        Effective wavelength (typically 0.1 to 2)
    """
    # Dominant scale normalized to ~[0.1, 2]
    t = max(cadence_days, 1.0)/7.0
    x = max(spatial_scale_km, 0.1)/1.0
    return 0.5*(t+x)


def estimate_k1(residual_std: float, ops_variance: float, habituation_rate: float) -> float:
    """
    Estimate process factor k1
    
    Args:
        residual_std: Standard deviation of model residuals
        ops_variance: Operational variance
        habituation_rate: Rate of habituation/adaptation
        
    Returns:
        Process factor k1 (typically 0.2 to 2.0)
    """
    return np.clip(0.3 + 0.7*np.tanh(residual_std + ops_variance + 2*habituation_rate), 0.2, 2.0)


def min_resolvable_deltaY(na_eff: float, lam_eff: float, k1: float) -> float:
    """
    Calculate minimum resolvable change (ΔY_min)
    
    Args:
        na_eff: Effective numerical aperture
        lam_eff: Effective wavelength
        k1: Process factor
        
    Returns:
        Minimum resolvable change (0.001 to 1.0)
    """
    if na_eff <= 1e-6: 
        return 1.0
    return np.clip(k1 * lam_eff / na_eff, 0.001, 1.0)


class ParameterEstimator:
    """
    Parameter estimation for resolution systems (class-based interface)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize estimator with configuration"""
        self.config = config
    
    def estimate_NA_eff(self, logs: List[Dict[str, Any]]) -> float:
        """
        Estimate effective NA parameter from system logs
        Coming soon - log-based NA_eff estimation implementation
        """
        # TODO: Implement log-based estimation
        # For now, use config-based estimation
        return estimate_na_eff(
            self.config.get('sensing_features', 5),
            self.config.get('actuation_channels', 3),
            self.config.get('feedback_latency_days', 1.0)
        )
    
    def estimate_lambda_eff(self, logs: List[Dict[str, Any]]) -> float:
        """
        Estimate effective lambda parameter from system logs
        Coming soon - log-based λ_eff estimation implementation
        """
        # TODO: Implement log-based estimation
        return estimate_lambda_eff(
            self.config.get('cadence_days', 7.0),
            self.config.get('spatial_scale_km', 1.0)
        )
    
    def estimate_k1(self, logs: List[Dict[str, Any]]) -> float:
        """
        Estimate k1 parameter from system logs
        Coming soon - log-based k1 estimation implementation
        """
        # TODO: Implement log-based estimation
        return estimate_k1(
            self.config.get('residual_std', 0.05),
            self.config.get('ops_variance', 0.03),
            self.config.get('habituation_rate', 0.02)
        )
    
    def estimate_all_parameters(self, logs: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Estimate all system parameters from logs
        """
        return {
            'NA_eff': self.estimate_NA_eff(logs),
            'lambda_eff': self.estimate_lambda_eff(logs), 
            'k1': self.estimate_k1(logs)
        }
