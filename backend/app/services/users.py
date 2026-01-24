from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.db.models.user import User


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    res = await session.execute(select(User).where(User.username == username))
    return res.scalar_one_or_none()


async def authenticate_user(session: AsyncSession, username: str, password: str) -> dict | None:
    user = await get_user_by_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return {"id": user.id, "username": user.username, "role": user.role}


async def ensure_seed_users(session: AsyncSession) -> None:
    res = await session.execute(select(func.count()).select_from(User))
    count = int(res.scalar_one())
    if count > 0:
        return

    session.add_all(
        [
            User(username="admin", password_hash=hash_password("admin123"), role="admin"),
            User(username="analyst", password_hash=hash_password("analyst123"), role="analyst"),
            User(username="viewer", password_hash=hash_password("viewer123"), role="viewer"),
        ]
    )
