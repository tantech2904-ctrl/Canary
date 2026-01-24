from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Float, Boolean
from ..base import Base, TimestampMixin

class Mitigation(Base, TimestampMixin):
    __tablename__ = "mitigations"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    suggestion: Mapped[str] = mapped_column(String(255))
    confidence: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(20))
    reversible: Mapped[bool] = mapped_column(Boolean, default=True)
    explanation: Mapped[str] = mapped_column(String(255))
    approved: Mapped[bool] = mapped_column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "suggestion": self.suggestion,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "reversible": self.reversible,
            "explanation": self.explanation,
            "approved": self.approved,
        }
