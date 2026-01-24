"""
Canary-Early warning system for computational systems
"""

__version__ = "0.1.0"
__author__ = "Radiothon Team"
__description__ = "Bayesian change-point detection with human-in-the-loop mitigation"

from .detector import BayesianChangePointDetector
from .early_signals import EarlyWarningAnalyzer
from .mitigator import MitigationEngine
from .simulator import RegimeShiftSimulator
from .utils import load_metrics, save_results, plot_timeseries