"""
Bayesian Change-Point Detection
Fixed version with proper error handling
"""

import numpy as np
from scipy import stats
from typing import Tuple, List, Dict, Optional
import warnings

class BayesianChangePointDetector:
    """
    Bayesian change-point detection for time-series data.
    """
    
    def __init__(self, hazard_rate: float = 0.01, threshold: float = 0.7):
        """
        Initialize detector.
        
        Args:
            hazard_rate: Probability of change at each step
            threshold: Probability threshold for declaring change point
        """
        self.hazard_rate = hazard_rate
        self.threshold = threshold
        self.reset()
        
    def reset(self):
        """Reset detector state."""
        self.observations = []
        self.change_points = []
        self.probabilities = []
        
        # Track sufficient statistics for current regime
        self.current_sum = 0.0
        self.current_sum_sq = 0.0
        self.current_count = 0
        
    def _safe_pdf(self, x: float, loc: float = 0, scale: float = 1) -> float:
        """
        Safe PDF calculation that handles edge cases.
        
        Returns:
            Probability density, clamped to reasonable values
        """
        if scale <= 0 or np.isnan(scale) or np.isinf(scale):
            # Fallback to uniform distribution
            return 1.0
        
        try:
            # Use normal distribution for simplicity
            pdf = stats.norm.pdf(x, loc=loc, scale=scale)
            # Ensure we don't get extremely small or large values
            return max(1e-10, min(pdf, 1e10))
        except:
            # Fallback
            return 1.0
    
    def update_sufficient_statistics(self, x: float):
        """Update mean and variance incrementally."""
        self.current_count += 1
        self.current_sum += x
        self.current_sum_sq += x * x
    
    def get_current_stats(self) -> Tuple[float, float]:
        """Get current mean and variance."""
        if self.current_count == 0:
            return 0.0, 1.0
        
        mean = self.current_sum / self.current_count
        
        if self.current_count > 1:
            variance = (self.current_sum_sq - self.current_sum * mean) / (self.current_count - 1)
            variance = max(1e-10, variance)  # Prevent zero variance
        else:
            variance = 1.0
            
        return mean, variance
    
    def predictive_probability(self, x: float) -> float:
        """
        Probability of observing x given current regime.
        Uses normal distribution for stability.
        """
        if self.current_count == 0:
            # Prior: normal with mean 0, variance 1
            return self._safe_pdf(x, loc=0, scale=1)
        
        mean, variance = self.get_current_stats()
        
        # Scale variance based on sample size (Bayesian uncertainty)
        scale = np.sqrt(variance * (1 + 1 / max(1, self.current_count)))
        
        return self._safe_pdf(x, loc=mean, scale=scale)
    
    def update(self, x: float) -> Tuple[bool, float]:
        # Store the new observation first
        self.observations.append(x)
        
        # Initialize probability
        change_prob = 0.0
        
        if len(self.observations) >= 2:  # Need at least 2 points for comparison
            # Calculate statistics for two windows
            
            # Window 1: Recent history (excluding current point)
            lookback = min(20, len(self.observations) - 1)
            if lookback >= 5:  # Need enough data for meaningful statistics
                # Previous window (old regime)
                prev_window = self.observations[-lookback-1:-1]  # Points before x
                
                # Current window (potential new regime) - just the current point
                # For a more robust approach, we could consider a small current window
                current_window = self.observations[-min(5, len(self.observations)):]  # Last few points including x
                
                # Calculate statistics
                prev_mean = np.mean(prev_window)
                prev_var = np.var(prev_window) if len(prev_window) > 1 else 1.0
                prev_var = max(1e-10, prev_var)
                
                current_mean = np.mean(current_window)
                current_var = np.var(current_window) if len(current_window) > 1 else 1.0
                current_var = max(1e-10, current_var)
                
                # Probability that x comes from old regime
                prob_old = self._safe_pdf(x, loc=prev_mean, scale=np.sqrt(prev_var))
                
                # Probability that x comes from new regime (starting recently)
                prob_new = self._safe_pdf(x, loc=current_mean, scale=np.sqrt(current_var))
                
                # Bayesian update with hazard rate as prior
                prior_change = self.hazard_rate
                prior_no_change = 1 - self.hazard_rate
                
                # Ensure non-zero probabilities
                prob_old = max(1e-10, prob_old)
                prob_new = max(1e-10, prob_new)
                
                # Calculate posterior probability of change
                # P(change | x) = P(x | change) * P(change) / [P(x | change)*P(change) + P(x | no_change)*P(no_change)]
                numerator = prob_new * prior_change
                denominator = numerator + prob_old * prior_no_change
                
                if denominator > 0:
                    change_prob = numerator / denominator
                
                # Alternative approach: Compare the two windows directly
                # Use likelihood ratio instead of just single point
                
                if len(prev_window) >= 5 and len(current_window) >= 3:
                    # More robust: Compare full distributions
                    # Simple approach: t-test-like comparison
                    n1, n2 = len(prev_window), len(current_window)
                    pooled_var = ((n1-1)*prev_var + (n2-1)*current_var) / (n1 + n2 - 2)
                    pooled_var = max(1e-10, pooled_var)
                    
                    # Effect size
                    effect_size = abs(prev_mean - current_mean) / np.sqrt(pooled_var)
                    
                    # Convert to probability (simplified)
                    # effect_size > 2 suggests high probability of change
                    prob_from_effect = min(1.0, effect_size / 4.0)
                    
                    # Combine both estimates
                    change_prob = 0.7 * change_prob + 0.3 * prob_from_effect
        
        # Clamp probability
        change_prob = max(0.0, min(1.0, change_prob))
        self.probabilities.append(change_prob)
        
        # Check if this is a change point
        is_change = bool(change_prob > self.threshold)
        
        if is_change:
            self.change_points.append(len(self.observations) - 1)
            # Reset statistics for new regime starting at current point
            self.current_sum = x
            self.current_sum_sq = x * x
            self.current_count = 1
        else:
            # Update statistics for current regime
            self.update_sufficient_statistics(x)
        
        return is_change, change_prob
        
    def detect_offline(self, data: np.ndarray) -> Dict:
        """
        Detect change points in offline data.
        
        Args:
            data: Time-series array
            
        Returns:
            Dictionary with detection results
            
        Raises:
            ValueError: If data is empty
        """
        if len(data) == 0:
            raise ValueError("Input data cannot be empty")
        
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        
        # Handle NaN/inf values
        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            warnings.warn("Data contains NaN or inf values, replacing with nearest valid values")
            data = np.array(data, dtype=np.float64)
            # Forward fill for NaN
            mask = np.isnan(data)
            indices = np.where(~mask, np.arange(len(data)), 0)
            np.maximum.accumulate(indices, out=indices)
            data = data[indices]
            # Replace inf with large finite values
            data[np.isinf(data)] = np.nan
            data = np.nan_to_num(data, nan=0.0, posinf=1e10, neginf=-1e10)
        
        self.reset()
        
        change_points = []
        probabilities = []
        
        for i, x in enumerate(data):
            is_change, prob = self.update(x)
            probabilities.append(prob)
            if is_change:
                change_points.append(i)
        
        return {
            'change_points': np.array(change_points),
            'probabilities': np.array(probabilities),
            'data': np.array(data)
        }
    
    def get_confidence_intervals(self, window_size: int = 10) -> np.ndarray:
        """
        Compute confidence intervals for change point probabilities.
        
        Args:
            window_size: Size of sliding window
            
        Returns:
            Array of (lower, upper) confidence bounds
        """
        if len(self.probabilities) < window_size:
            return np.array([[0, 1]] * len(self.probabilities))
        
        conf_intervals = []
        probs = np.array(self.probabilities)
        
        for i in range(len(probs)):
            start = max(0, i - window_size // 2)
            end = min(len(probs), i + window_size // 2)
            window = probs[start:end]
            
            if len(window) > 0 and np.std(window) > 0:
                mean = np.mean(window)
                std = np.std(window)
                conf_intervals.append([
                    max(0, mean - 1.96 * std / np.sqrt(len(window))),
                    min(1, mean + 1.96 * std / np.sqrt(len(window)))
                ])
            else:
                conf_intervals.append([0, 1])
        
        return np.array(conf_intervals)