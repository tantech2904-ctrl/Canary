from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import require_role
from app.db.session import async_session
from app.db.models.audit import AuditLog

router = APIRouter()

@router.get("/audit/logs")
async def audit_logs(
    limit: int = 500,
    run_id: int | None = None,
    user_id: int | None = None,
    action: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    user=Depends(require_role("analyst")),
):
    limit = min(max(limit, 1), 2000)
    async with async_session() as session:  # type: AsyncSession
        stmt = select(AuditLog)
        if run_id is not None:
            stmt = stmt.where(AuditLog.run_id == run_id)
        if user_id is not None:
            stmt = stmt.where(AuditLog.user_id == user_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        if since is not None:
            stmt = stmt.where(AuditLog.created_at >= since)
        if until is not None:
            stmt = stmt.where(AuditLog.created_at <= until)

        res = await session.execute(stmt.order_by(AuditLog.created_at.desc()).limit(limit))
        logs = [a.to_dict() for a in res.scalars().all()]
    return {"logs": logs}
