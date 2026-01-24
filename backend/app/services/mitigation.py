from typing import List, Dict

THRESHOLDS = {
    "high": 0.9,
    "medium": 0.8,
}

SUGGESTIONS = [
    {
        "suggestion": "Reduce learning rate by 20%",
        "risk_level": "medium",
        "reversible": True,
        "explanation": "Mean shift indicates instability; lowering LR can help.",
    },
    {
        "suggestion": "Rollback to last stable checkpoint",
        "risk_level": "high",
        "reversible": True,
        "explanation": "Posterior mass near recent change suggests regression.",
    },
    {
        "suggestion": "Increase batch size",
        "risk_level": "low",
        "reversible": True,
        "explanation": "Variance shift indicates noise; larger batch can stabilize.",
    },
]


def suggest_mitigations(run_id: int, confidence: float = 0.85) -> List[Dict]:
    # Confidence-gated: include higher risk options only when confidence is strong
    items: List[Dict] = []
    for s in SUGGESTIONS:
        include = confidence >= THRESHOLDS.get(s["risk_level"], 0.8)
        if include:
            items.append({
                "run_id": run_id,
                "suggestion": s["suggestion"],
                "confidence": confidence,
                "risk_level": s["risk_level"],
                "reversible": s["reversible"],
                "explanation": s["explanation"],
                "approved": False,
            })
    return items
