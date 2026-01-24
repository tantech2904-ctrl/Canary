from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
from ..base import Base, TimestampMixin

class Run(Base, TimestampMixin):
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(Text, default="")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}
