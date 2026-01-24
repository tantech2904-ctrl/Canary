from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, JSON
from ..base import Base, TimestampMixin

class Analysis(Base, TimestampMixin):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    result: Mapped[dict] = mapped_column(JSON)
