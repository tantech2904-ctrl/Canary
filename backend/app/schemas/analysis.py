from pydantic import BaseModel
from typing import List

class AnalysisOverview(BaseModel):
    run_id: int
    change_points: List[int]
    probabilities: List[float]
