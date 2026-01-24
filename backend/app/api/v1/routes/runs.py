from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.db.session import async_session
from app.db.models.run import Run

router = APIRouter()

@router.get("/runs")
async def list_runs(user=Depends(get_current_user)):
    async with async_session() as session:  # type: AsyncSession
        res = await session.execute(select(Run).order_by(Run.created_at.desc()))
        runs = [
            {"id": r.id, "name": r.name, "description": r.description, "created_at": r.created_at.isoformat()}
            for r in res.scalars().all()
        ]
    return {"runs": runs}
