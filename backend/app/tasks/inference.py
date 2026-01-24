from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from ..db.session import async_session
from ..db.models.metric import Metric
from ..db.models.analysis import Analysis
from ..services.bayesian.offline_pymc import OfflinePosterior

async def enqueue_offline_posterior(run_id: int, bg: BackgroundTasks):
    bg.add_task(run_offline_posterior, run_id)

async def run_offline_posterior(run_id: int):
    async with async_session() as session:  # type: AsyncSession
        res = await session.execute(select(Metric).where(Metric.run_id == run_id).order_by(Metric.timestamp.asc()))
        data = [m.value for m in res.scalars().all()]
        posterior_engine = OfflinePosterior(seed=42)
        result = posterior_engine.compute(data)
        await session.execute(insert(Analysis).values(run_id=run_id, result=result))
        await session.commit()
