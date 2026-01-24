from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from ..db.models.audit import AuditLog

async def log_approval(session: AsyncSession, user_id: int, run_id: int, mitigation_id: int):
    await session.execute(insert(AuditLog).values(
        user_id=user_id,
        run_id=run_id,
        action="approve_mitigation",
        details={"mitigation_id": mitigation_id},
    ))
    await session.commit()
