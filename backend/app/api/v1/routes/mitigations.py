from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

from app.dependencies.auth import get_current_user, require_role
from app.db.session import async_session
from app.db.models.run import Run
from app.db.models.mitigation import Mitigation
from app.services.mitigation import suggest_mitigations
from app.services.audit import log_approval

router = APIRouter()

@router.get("/mitigations/{run_id}")
async def list_mitigations(run_id: int, user=Depends(get_current_user)):
    async with async_session() as session:  # type: AsyncSession
        run = await session.get(Run, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        res = await session.execute(select(Mitigation).where(Mitigation.run_id == run_id))
        items = [m.to_dict() for m in res.scalars().all()]
        if not items:
            # generate suggestions on-demand
            items = suggest_mitigations(run_id)
            await session.execute(insert(Mitigation), items)
            await session.commit()
    return {"mitigations": items}

@router.post("/mitigations/{run_id}/approve")
async def approve_mitigation(run_id: int, mitigation_id: int, user=Depends(require_role("analyst"))):
    async with async_session() as session:
        run = await session.get(Run, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        mitigation = await session.get(Mitigation, mitigation_id)
        if not mitigation:
            raise HTTPException(status_code=404, detail="Mitigation not found")
        mitigation.approved = True
        await session.commit()
        await log_approval(session, user_id=user["id"], run_id=run_id, mitigation_id=mitigation_id)
    return {"status": "approved"}
