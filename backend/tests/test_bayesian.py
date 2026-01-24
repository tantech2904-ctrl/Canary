import math
from app.services.bayesian.online_cpd import OnlineCPD

def test_online_cpd_detects_mean_shift():
    # Synthetic: constant 0 then shift to 3
    series = [(i, 0.0) for i in range(50)] + [(50+i, 3.0) for i in range(50)]
    cpd = OnlineCPD(seed=123)
    cpd.fit(series)
    assert any(cp >= 45 for cp in cpd.change_points), "Should detect a change near the shift"
    assert max(cpd.probabilities) > 0.9
