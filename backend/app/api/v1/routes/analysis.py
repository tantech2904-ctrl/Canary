from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.db.session import async_session
from app.db.models.run import Run
from app.db.models.metric import Metric
from app.services.bayesian.online_cpd import OnlineCPD
from app.services.bayesian.offline_pymc import OfflinePosterior

router = APIRouter()

@router.get("/analysis/{run_id}")
async def analysis_overview(run_id: int, user=Depends(get_current_user)):
    async with async_session() as session:  # type: AsyncSession
        run = await session.get(Run, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        res = await session.execute(select(Metric).where(Metric.run_id == run_id).order_by(Metric.timestamp.asc()))
        metrics = [(m.timestamp.timestamp(), m.value) for m in res.scalars().all()]
    online = OnlineCPD(seed=42)
    online.fit(metrics)
    return {
        "run_id": run_id,
        "change_points": online.change_points,
        "probabilities": online.probabilities,
    }

@router.get("/analysis/{run_id}/posterior")
async def posterior(run_id: int, user=Depends(get_current_user)):
    async with async_session() as session:
        run = await session.get(Run, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        res = await session.execute(select(Metric).where(Metric.run_id == run_id).order_by(Metric.timestamp.asc()))
        data = [m.value for m in res.scalars().all()]
    posterior_engine = OfflinePosterior(seed=42)
    posterior = posterior_engine.compute(data)
    return posterior
