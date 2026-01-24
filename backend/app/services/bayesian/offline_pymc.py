from typing import Dict, List
import numpy as np
try:
    import pymc as pm
    import aesara.tensor as at
except Exception:
    pm = None

class OfflinePosterior:
    """Offline Bayesian posterior over a single change point (mean shift)."""
    def __init__(self, seed: int = 42):
        self.seed = seed

    def compute(self, data: List[float]) -> Dict:
        arr = np.asarray(data, dtype=float)
        n = len(arr)
        if n < 10 or pm is None:
            # Fallback: simple normal estimates and heuristic CI
            mu = float(arr.mean())
            sigma = float(arr.std() + 1e-6)
            return {
                "method": "heuristic",
                "mean": mu,
                "sigma": sigma,
                "credible_interval": [mu - 1.96 * sigma / np.sqrt(max(n,1)), mu + 1.96 * sigma / np.sqrt(max(n,1))],
                "cp_posterior": [0.0] * n,
            }
        with pm.Model() as model:
            cp = pm.DiscreteUniform("cp", lower=1, upper=n-2)
            mu1 = pm.Normal("mu1", mu=arr.mean(), sigma=arr.std() + 1e-6)
            mu2 = pm.Normal("mu2", mu=arr.mean(), sigma=arr.std() + 1e-6)
            sigma = pm.HalfNormal("sigma", sigma=max(arr.std(), 1e-3))
            idx = at.arange(n)
            mu = at.switch(idx <= cp, mu1, mu2)
            pm.Normal("y", mu=mu, sigma=sigma, observed=arr)
            trace = pm.sample(1000, tune=1000, random_seed=self.seed, chains=2, cores=1, progressbar=False)
        cp_samples = trace.posterior["cp"].values.reshape(-1)
        hist = np.bincount(cp_samples, minlength=n)
        cp_posterior = (hist / hist.sum()).tolist()
        mu1_mean = float(trace.posterior["mu1"].mean().values)
        mu2_mean = float(trace.posterior["mu2"].mean().values)
        return {
            "method": "pymc",
            "cp_posterior": cp_posterior,
            "mu1": mu1_mean,
            "mu2": mu2_mean,
        }
