import argparse
import json
from datetime import datetime, timedelta, timezone

import numpy as np


def generate_mean_shift(n1: int, n2: int, mu1: float, mu2: float, sigma: float, seed: int):
    rng = np.random.default_rng(seed)
    a = rng.normal(mu1, sigma, size=n1)
    b = rng.normal(mu2, sigma, size=n2)
    return np.concatenate([a, b]).tolist()


def main():
    p = argparse.ArgumentParser(description="Generate synthetic regime-shift time series payload.")
    p.add_argument('--run-name', default='synthetic-mean-shift')
    p.add_argument('--n1', type=int, default=120)
    p.add_argument('--n2', type=int, default=120)
    p.add_argument('--mu1', type=float, default=0.0)
    p.add_argument('--mu2', type=float, default=2.5)
    p.add_argument('--sigma', type=float, default=0.4)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--out', default='datasets/synthetic/run_mean_shift.json')
    args = p.parse_args()

    values = generate_mean_shift(args.n1, args.n2, args.mu1, args.mu2, args.sigma, args.seed)

    start = datetime.now(timezone.utc) - timedelta(minutes=len(values))
    metrics = []
    for i, v in enumerate(values):
        ts = start + timedelta(minutes=i)
        metrics.append({
            "timestamp": ts.isoformat(),
            "value": float(v),
        })

    payload = {
        "run_name": args.run_name,
        "description": f"Synthetic mean shift: mu {args.mu1} -> {args.mu2}, sigma {args.sigma}, seed {args.seed}",
        "metrics": metrics,
    }

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote {args.out} with {len(metrics)} points")


if __name__ == '__main__':
    main()
