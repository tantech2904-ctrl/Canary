from pydantic import BaseModel

class MitigationOut(BaseModel):
    id: int
    run_id: int
    suggestion: str
    confidence: float
    risk_level: str
    reversible: bool
    explanation: str
    approved: bool
