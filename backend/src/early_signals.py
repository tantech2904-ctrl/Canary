import numpy as np
from scipy import stats, signal
from typing import List, Dict, Tuple
import warnings

class EarlyWarningAnalyzer:
    """
    Analyzes time-series for early warning signals of regime shifts.
    
    Based on resilience theory and critical slowing down indicators.
    """
    
    def __init__(self, window_size: int = 20, step_size: int = 5):
        """
        Initialize analyzer.
        
        Args:
            window_size: Size of sliding window for statistics
            step_size: Step between windows
        """
        self.window_size = window_size
        self.step_size = step_size
        
    def compute_variance(self, data: np.ndarray) -> np.ndarray:
        """
        Compute rolling variance.
        
        Increasing variance is an early warning signal.
        """
        n = len(data)
        variances = []
        
        for i in range(0, n - self.window_size + 1, self.step_size):
            window = data[i:i + self.window_size]
            variances.append(np.var(window))
        
        return np.array(variances)
    
    def compute_autocorrelation(self, data: np.ndarray, lag: int = 1) -> np.ndarray:
        """
        Compute rolling autocorrelation.
        
        Increasing autocorrelation indicates critical slowing down.
        """
        n = len(data)
        autocorrs = []
        
        for i in range(0, n - self.window_size + 1, self.step_size):
            window = data[i:i + self.window_size]
            if len(window) > lag:
                corr = np.corrcoef(window[:-lag], window[lag:])[0, 1]
                autocorrs.append(corr if not np.isnan(corr) else 0)
            else:
                autocorrs.append(0)
        
        return np.array(autocorrs)
    
    def compute_skewness(self, data: np.ndarray) -> np.ndarray:
        """
        Compute rolling skewness.
        
        Changing skewness indicates distribution shifts.
        """
        n = len(data)
        skews = []
        
        for i in range(0, n - self.window_size + 1, self.step_size):
            window = data[i:i + self.window_size]
            skews.append(stats.skew(window))
        
        return np.array(skews)
    
    def compute_return_rate(self, data: np.ndarray, threshold: float = 0.1) -> np.ndarray:
        """
        Compute rate of return to mean.
        
        Slower return rates indicate loss of resilience.
        """
        n = len(data)
        mean = np.mean(data)
        returns = []
        
        crossing_indices = []
        for i in range(1, n):
            if (data[i-1] - mean) * (data[i] - mean) < 0:
                crossing_indices.append(i)
        
        if len(crossing_indices) < 2:
            return np.array([0])
        
        return_times = np.diff(crossing_indices)
        windowed_returns = []
        
        for i in range(0, len(return_times) - self.window_size//5 + 1, self.step_size//5):
            window = return_times[i:i + self.window_size//5]
            if len(window) > 0:
                windowed_returns.append(np.mean(window))
        
        return np.array(windowed_returns)
    
    def spectral_analysis(self, data: np.ndarray) -> Dict:
        """
        Perform spectral analysis for early warnings.
        
        Returns:
            Dictionary with spectral features
        """
        # Detrend
        detrended = signal.detrend(data)
        
        # Compute power spectrum
        freqs, psd = signal.welch(detrended, nperseg=min(256, len(data)//4))
        
        # Spectral ratio (low freq / high freq)
        low_freq_mask = freqs < 0.1
        high_freq_mask = freqs > 0.4
        
        if np.any(low_freq_mask) and np.any(high_freq_mask):
            low_power = np.mean(psd[low_freq_mask])
            high_power = np.mean(psd[high_freq_mask])
            spectral_ratio = low_power / (high_power + 1e-10)
        else:
            spectral_ratio = 1.0
        
        # Dominant frequency
        dominant_freq = freqs[np.argmax(psd)] if len(psd) > 0 else 0
        
        return {
            'frequencies': freqs,
            'power_spectrum': psd,
            'spectral_ratio': spectral_ratio,
            'dominant_frequency': dominant_freq,
            'total_power': np.sum(psd)
        }
    
    def analyze_early_signals(self, data: np.ndarray) -> Dict:
        """
        Comprehensive early warning signal analysis.
        
        Returns:
            Dictionary with all warning signals
        """
        warnings_dict = {}
        
        # Basic statistics
        warnings_dict['variance'] = self.compute_variance(data)
        warnings_dict['autocorrelation'] = self.compute_autocorrelation(data)
        warnings_dict['skewness'] = self.compute_skewness(data)
        warnings_dict['return_rate'] = self.compute_return_rate(data)
        
        # Trend analysis
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            variance_trend = stats.linregress(
                np.arange(len(warnings_dict['variance'])), 
                warnings_dict['variance']
            ).slope if len(warnings_dict['variance']) > 1 else 0
            
            autocorr_trend = stats.linregress(
                np.arange(len(warnings_dict['autocorrelation'])), 
                warnings_dict['autocorrelation']
            ).slope if len(warnings_dict['autocorrelation']) > 1 else 0
        
        # Spectral analysis
        spectral = self.spectral_analysis(data)
        
        # Composite warning score
        warning_score = 0
        if variance_trend > 0:
            warning_score += 0.3
        if autocorr_trend > 0:
            warning_score += 0.3
        if spectral['spectral_ratio'] > 2:
            warning_score += 0.2
        if len(warnings_dict['return_rate']) > 0 and np.mean(warnings_dict['return_rate']) > 20:
            warning_score += 0.2
        
        warnings_dict['warning_score'] = min(1.0, warning_score)
        warnings_dict['variance_trend'] = variance_trend
        warnings_dict['autocorrelation_trend'] = autocorr_trend
        warnings_dict['spectral'] = spectral
        
        return warnings_dict
    
    def predict_regime_shift(self, data: np.ndarray, 
                           warning_threshold: float = 0.6) -> Tuple[bool, float, Dict]:
        """
        Predict likelihood of imminent regime shift.
        
        Returns:
            Tuple of (is_warning, confidence, signals)
        """
        signals = self.analyze_early_signals(data)
        warning_score = signals['warning_score']
        
        is_warning = warning_score > warning_threshold
        
        # Confidence based on signal consistency
        confidence = warning_score
        if signals['variance_trend'] > 0 and signals['autocorrelation_trend'] > 0:
            confidence *= 1.2  # Boost if multiple signals agree
        
        return is_warning, min(1.0, confidence), signals