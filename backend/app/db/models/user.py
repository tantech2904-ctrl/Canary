from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from ..base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20), default="viewer")

    def to_dict(self):
        return {"id": self.id, "username": self.username, "role": self.role}
