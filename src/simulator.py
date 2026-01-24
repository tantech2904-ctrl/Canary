"""
Regime Shift Simulator
Generates synthetic time-series data with regime shifts
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import warnings

class RegimeType(Enum):
    """Types of regime shifts."""
    MEAN_SHIFT = "mean_shift"
    VARIANCE_SHIFT = "variance_shift"
    TREND_SHIFT = "trend_shift"
    PERIODICITY_SHIFT = "periodicity_shift"
    DISTRIBUTION_SHIFT = "distribution_shift"
    COMPLEX = "complex"

@dataclass
class RegimeConfig:
    """Configuration for a regime."""
    start_idx: int
    end_idx: int
    regime_type: RegimeType
    params: Dict
    
class RegimeShiftSimulator:
    """
    Simulates time-series data with multiple regime shifts.
    """
    
    def __init__(self, seed: Optional[int] = 42):
        """
        Initialize simulator.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)
        
    def generate_mean_shift(self, n_points: int = 1000, 
                           shift_times: List[int] = [300, 600],
                           means: List[float] = [0, 2, -1],
                           variance: float = 1.0) -> Tuple[np.ndarray, List[RegimeConfig]]:
        """
        Generate data with mean shifts.
        
        Args:
            n_points: Total number of points
            shift_times: Indices where shifts occur
            means: Mean values for each regime
            variance: Noise variance
            
        Returns:
            Tuple of (data, regime_configs)
        """
        data = np.zeros(n_points)
        regimes = []
        
        # Add initial regime
        start_idx = 0
        regime_idx = 0
        
        all_shifts = sorted(shift_times) + [n_points]
        
        for end_idx in all_shifts:
            if regime_idx < len(means):
                mean = means[regime_idx]
                regime_data = mean + np.random.randn(end_idx - start_idx) * np.sqrt(variance)
                data[start_idx:end_idx] = regime_data
                
                regimes.append(RegimeConfig(
                    start_idx=start_idx,
                    end_idx=end_idx,
                    regime_type=RegimeType.MEAN_SHIFT,
                    params={"mean": mean, "variance": variance}
                ))
                
                start_idx = end_idx
                regime_idx += 1
        
        return data, regimes
    
    def generate_variance_shift(self, n_points: int = 1000,
                              shift_times: List[int] = [300, 600],
                              variances: List[float] = [1.0, 4.0, 0.25],
                              mean: float = 0.0) -> Tuple[np.ndarray, List[RegimeConfig]]:
        """
        Generate data with variance shifts.
        
        Args:
            n_points: Total number of points
            shift_times: Indices where shifts occur
            variances: Variance values for each regime
            mean: Constant mean
            
        Returns:
            Tuple of (data, regime_configs)
        """
        data = np.zeros(n_points)
        regimes = []
        
        start_idx = 0
        regime_idx = 0
        
        all_shifts = sorted(shift_times) + [n_points]
        
        for end_idx in all_shifts:
            if regime_idx < len(variances):
                variance = variances[regime_idx]
                regime_data = mean + np.random.randn(end_idx - start_idx) * np.sqrt(variance)
                data[start_idx:end_idx] = regime_data
                
                regimes.append(RegimeConfig(
                    start_idx=start_idx,
                    end_idx=end_idx,
                    regime_type=RegimeType.VARIANCE_SHIFT,
                    params={"mean": mean, "variance": variance}
                ))
                
                start_idx = end_idx
                regime_idx += 1
        
        return data, regimes
    
    def generate_trend_shift(self, n_points: int = 1000,
                           shift_times: List[int] = [300, 600],
                           slopes: List[float] = [0.01, -0.02, 0.005],
                           intercepts: List[float] = [0, 5, 2],
                           noise_std: float = 0.5) -> Tuple[np.ndarray, List[RegimeConfig]]:
        """
        Generate data with trend shifts.
        
        Args:
            n_points: Total number of points
            shift_times: Indices where shifts occur
            slopes: Slope for each regime
            intercepts: Intercept for each regime
            noise_std: Noise standard deviation
            
        Returns:
            Tuple of (data, regime_configs)
        """
        data = np.zeros(n_points)
        regimes = []
        
        start_idx = 0
        regime_idx = 0
        
        all_shifts = sorted(shift_times) + [n_points]
        
        for end_idx in all_shifts:
            if regime_idx < len(slopes) and regime_idx < len(intercepts):
                slope = slopes[regime_idx]
                intercept = intercepts[regime_idx]
                
                x = np.arange(end_idx - start_idx)
                trend = intercept + slope * x
                noise = np.random.randn(len(x)) * noise_std
                
                data[start_idx:end_idx] = trend + noise
                
                regimes.append(RegimeConfig(
                    start_idx=start_idx,
                    end_idx=end_idx,
                    regime_type=RegimeType.TREND_SHIFT,
                    params={"slope": slope, "intercept": intercept, "noise_std": noise_std}
                ))
                
                start_idx = end_idx
                regime_idx += 1
        
        return data, regimes
    
    def generate_periodic_shift(self, n_points: int = 1000,
                              shift_times: List[int] = [300, 600],
                              periods: List[float] = [50, 25, 100],
                              amplitudes: List[float] = [2.0, 1.0, 3.0],
                              noise_std: float = 0.3) -> Tuple[np.ndarray, List[RegimeConfig]]:
        """
        Generate data with periodicity shifts.
        
        Args:
            n_points: Total number of points
            shift_times: Indices where shifts occur
            periods: Period lengths for each regime
            amplitudes: Amplitudes for each regime
            noise_std: Noise standard deviation
            
        Returns:
            Tuple of (data, regime_configs)
        """
        data = np.zeros(n_points)
        regimes = []
        
        start_idx = 0
        regime_idx = 0
        
        all_shifts = sorted(shift_times) + [n_points]
        
        for end_idx in all_shifts:
            if regime_idx < len(periods) and regime_idx < len(amplitudes):
                period = periods[regime_idx]
                amplitude = amplitudes[regime_idx]
                
                x = np.arange(end_idx - start_idx)
                periodic = amplitude * np.sin(2 * np.pi * x / period)
                noise = np.random.randn(len(x)) * noise_std
                
                data[start_idx:end_idx] = periodic + noise
                
                regimes.append(RegimeConfig(
                    start_idx=start_idx,
                    end_idx=end_idx,
                    regime_type=RegimeType.PERIODICITY_SHIFT,
                    params={"period": period, "amplitude": amplitude, "noise_std": noise_std}
                ))
                
                start_idx = end_idx
                regime_idx += 1
        
        return data, regimes
    
    # In src/simulator.py, fix the generate_complex_shift method:

    def generate_complex_shift(self, n_points: int = 1000,shift_times: List[int] = None) -> Tuple[np.ndarray, List[RegimeConfig]]:
        if shift_times is None:
            shift_times = [n_points//5, 2*n_points//5, 3*n_points//5, 4*n_points//5]
        
        # Filter shift times to be within bounds
        shift_times = [t for t in shift_times if 0 < t < n_points]
        
        data = np.zeros(n_points)
        regimes = []
        
        # Add initial point
        start_idx = 0
        
        # Create regimes based on shift times
        all_bounds = sorted(shift_times) + [n_points]
        
        for regime_idx, end_idx in enumerate(all_bounds):
            if start_idx >= end_idx:
                continue
                
            segment_length = end_idx - start_idx
            
            if regime_idx == 0:  # Stable low noise
                data[start_idx:end_idx] = 5 + np.random.randn(segment_length) * 0.5
                regimes.append(RegimeConfig(
                    start_idx=start_idx,
                    end_idx=end_idx,
                    regime_type=RegimeType.MEAN_SHIFT,
                    params={"mean": 5, "variance": 0.25}
                ))
                
            elif regime_idx == 1:  # Increasing trend
                x = np.arange(segment_length)
                data[start_idx:end_idx] = 3 + 0.02 * x + np.random.randn(segment_length) * 1.0
                regimes.append(RegimeConfig(
                    start_idx=start_idx,
                    end_idx=end_idx,
                    regime_type=RegimeType.TREND_SHIFT,
                    params={"slope": 0.02, "intercept": 3, "noise_std": 1.0}
                ))
                
            elif regime_idx == 2:  # High variance
                data[start_idx:end_idx] = 2 + np.random.randn(segment_length) * 2.0
                regimes.append(RegimeConfig(
                    start_idx=start_idx,
                    end_idx=end_idx,
                    regime_type=RegimeType.VARIANCE_SHIFT,
                    params={"mean": 2, "variance": 4.0}
                ))
                
            elif regime_idx == 3:  # Periodic pattern
                x = np.arange(segment_length)
                data[start_idx:end_idx] = 1 + 1.5 * np.sin(2 * np.pi * x / 40) + np.random.randn(segment_length) * 0.3
                regimes.append(RegimeConfig(
                    start_idx=start_idx,
                    end_idx=end_idx,
                    regime_type=RegimeType.PERIODICITY_SHIFT,
                    params={"period": 40, "amplitude": 1.5, "noise_std": 0.3}
                ))
                
            else:  # Drifting mean
                x = np.arange(segment_length)
                drift = 0.01 * x
                noise = np.random.randn(segment_length) * (0.5 + 0.001 * x)
                data[start_idx:end_idx] = 0 + drift + noise
                regimes.append(RegimeConfig(
                    start_idx=start_idx,
                    end_idx=end_idx,
                    regime_type=RegimeType.COMPLEX,
                    params={"drift": 0.01, "variance_growth": 0.001}
                ))
            
            start_idx = end_idx
        
        return data, regimes
    
    def add_outliers(self, data: np.ndarray, 
                    outlier_prob: float = 0.01,
                    outlier_magnitude: float = 5.0) -> np.ndarray:
        """
        Add outliers to data.
        
        Args:
            data: Input data
            outlier_prob: Probability of outlier at each point
            outlier_magnitude: How large outliers are (in std units)
            
        Returns:
            Data with outliers
        """
        data_with_outliers = data.copy()
        n = len(data)
        
        std = np.std(data)
        outlier_mask = np.random.rand(n) < outlier_prob
        
        # Add positive and negative outliers
        signs = np.random.choice([-1, 1], size=n)
        outliers = signs * outlier_magnitude * std
        
        data_with_outliers[outlier_mask] += outliers[outlier_mask]
        
        return data_with_outliers
    
    def add_missing_values(self, data: np.ndarray, 
                          missing_prob: float = 0.05) -> np.ndarray:
        """
        Add missing values (NaN) to data.
        
        Args:
            data: Input data
            missing_prob: Probability of missing value
            
        Returns:
            Data with NaN values
        """
        data_with_nan = data.copy()
        n = len(data)
        
        missing_mask = np.random.rand(n) < missing_prob
        data_with_nan[missing_mask] = np.nan
        
        return data_with_nan
    
    def simulate_ml_training(self, n_steps: int = 1000) -> Dict:
        """
        Simulate ML training metrics with realistic regime shifts.
        
        Returns:
            Dictionary with multiple metrics
        """
        metrics = {}
        
        # Training loss: typically decreases with occasional spikes
        base_loss = np.exp(-np.linspace(0, 5, n_steps))
        noise = np.random.randn(n_steps) * 0.1
        spikes = np.zeros(n_steps)
        spike_indices = [150, 450, 750]
        for idx in spike_indices:
            if idx < n_steps:
                spikes[idx:idx+20] = 0.5 * np.exp(-np.arange(20)/5)
        
        metrics['training_loss'] = base_loss + noise + spikes
        
        # Validation loss: similar but with generalization gap
        metrics['validation_loss'] = metrics['training_loss'] * 1.1 + np.random.randn(n_steps) * 0.15
        
        # Learning rate (if scheduled)
        metrics['learning_rate'] = 0.01 * np.exp(-np.linspace(0, 2, n_steps))
        
        # Gradient norm: shows optimization behavior
        metrics['gradient_norm'] = np.exp(-np.linspace(0, 3, n_steps)) + np.random.randn(n_steps) * 0.2
        # Add a spike
        metrics['gradient_norm'][300:320] += 1.0
        
        # Accuracy (for classification)
        metrics['training_accuracy'] = 1 - np.exp(-np.linspace(0, 4, n_steps)) + np.random.randn(n_steps) * 0.02
        metrics['validation_accuracy'] = metrics['training_accuracy'] * 0.95
        
        return metrics
    
    def generate_dataset(self, n_samples: int = 1000, 
                        dataset_type: str = "complex",
                        add_outliers: bool = True,
                        add_missing: bool = False,
                        seed: Optional[int] = None) -> pd.DataFrame:
        """
        Generate a complete dataset for testing.
        
        Args:
            n_samples: Number of samples
            dataset_type: Type of dataset ("mean_shift", "variance_shift", "complex", "ml_training")
            add_outliers: Whether to add outliers
            add_missing: Whether to add missing values
            seed: Random seed
            
        Returns:
            DataFrame with generated data
        """
        if seed is not None:
            np.random.seed(seed)
        
        if dataset_type == "ml_training":
            metrics = self.simulate_ml_training(n_samples)
            df = pd.DataFrame(metrics)
            df.index.name = "step"
            
        else:
            if dataset_type == "mean_shift":
                data, regimes = self.generate_mean_shift(n_samples)
                col_name = "value_mean_shift"
            elif dataset_type == "variance_shift":
                data, regimes = self.generate_variance_shift(n_samples)
                col_name = "value_variance_shift"
            elif dataset_type == "complex":
                data, regimes = self.generate_complex_shift(n_samples)
                col_name = "value_complex"
            else:
                raise ValueError(f"Unknown dataset type: {dataset_type}")
            
            df = pd.DataFrame({col_name: data})
            df.index.name = "timestamp"
            
            # Add regime labels
            df['regime'] = 0
            for i, regime in enumerate(regimes):
                df.loc[regime.start_idx:regime.end_idx-1, 'regime'] = i + 1
            df['regime_type'] = df['regime'].apply(lambda x: regimes[x-1].regime_type.value if x > 0 else "none")
        
        # Add outliers if requested
        if add_outliers and dataset_type != "ml_training":
            for col in df.columns:
                if col not in ['regime', 'regime_type']:
                    df[col] = self.add_outliers(df[col].values)
        
        # Add missing values if requested
        if add_missing and dataset_type != "ml_training":
            for col in df.columns:
                if col not in ['regime', 'regime_type']:
                    df[col] = self.add_missing_values(df[col].values)
        
        return df
    
    def save_dataset(self, df: pd.DataFrame, path: str):
        """
        Save dataset to CSV.
        
        Args:
            df: DataFrame to save
            path: Path to save CSV
        """
        df.to_csv(path, index=True)
        print(f"Dataset saved to {path} (shape: {df.shape})")

if __name__ == "__main__":
    # Example usage
    simulator = RegimeShiftSimulator(seed=42)
    
    # Generate complex dataset
    df = simulator.generate_dataset(
        n_samples=1000,
        dataset_type="complex",
        add_outliers=True,
        add_missing=False
    )
    
    # Save to CSV
    simulator.save_dataset(df, "demo/sample_data.csv")
    
    print("Dataset columns:", df.columns.tolist())
    print("First few rows:")
    print(df.head())