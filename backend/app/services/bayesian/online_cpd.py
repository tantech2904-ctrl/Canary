import numpy as np
from typing import List, Tuple

class OnlineCPD:
    """Simple online Bayesian change-point detector for mean shifts.
    Returns per-step probability of a change-point using a hazard function.
    """
    def __init__(self, hazard: float = 1/200.0, seed: int = 42):
        self.hazard = hazard
        self.rng = np.random.default_rng(seed)
        self.change_points: List[int] = []
        self.probabilities: List[float] = []

    def fit(self, series: List[Tuple[float, float]]):
        values = np.array([v for _, v in series], dtype=float)
        n = len(values)
        if n < 5:
            self.change_points = []
            self.probabilities = [0.0] * n
            return
        mean_prev = values[0]
        var_prev = np.var(values[:5]) + 1e-6
        probs = []
        cps = []
        for i in range(n):
            x = values[i]
            # Gaussian predictive under previous regime
            ll_same = -0.5 * ((x - mean_prev) ** 2) / var_prev
            # Hypothetical new regime: mean reset to x, higher uncertainty
            ll_new = -0.5 * ((x - x) ** 2) / (var_prev * 2)
            p_new = 1 / (1 + np.exp(ll_same - ll_new))
            # Combine with hazard
            p_cp = min(0.999, max(0.0, self.hazard + (1 - self.hazard) * p_new))
            probs.append(float(p_cp))
            if p_cp > 0.9:
                cps.append(i)
                mean_prev = x
            else:
                # exponential moving average for mean
                mean_prev = 0.98 * mean_prev + 0.02 * x
        self.change_points = cps
        self.probabilities = probs
