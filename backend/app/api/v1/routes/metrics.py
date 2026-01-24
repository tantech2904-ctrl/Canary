from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select

from app.schemas.metrics import MetricsUpload, MetricsStreamItem, MetricsStreamResponse
from app.dependencies.auth import get_current_user
from app.db.session import async_session
from app.db.models.metric import Metric
from app.db.models.run import Run
from app.tasks.inference import enqueue_offline_posterior

router = APIRouter()

@router.post("/metrics/upload")
async def upload_metrics(payload: MetricsUpload, user=Depends(get_current_user)):
    async with async_session() as session:  # type: AsyncSession
        # create run
        run_stmt = insert(Run).values(name=payload.run_name, description=payload.description).returning(Run.id)
        run_id_res = await session.execute(run_stmt)
        run_id = run_id_res.scalar_one()
        # bulk insert metrics
        metric_rows = [
            {"run_id": run_id, "timestamp": m.timestamp, "value": m.value}
            for m in payload.metrics
        ]
        await session.execute(insert(Metric), metric_rows)
        await session.commit()
    # kick off offline posterior computation (best-effort)
    try:
        from fastapi import BackgroundTasks
        bg = BackgroundTasks()
        await enqueue_offline_posterior(run_id, bg)
    except Exception:
        pass
    return {"run_id": run_id, "count": len(metric_rows)}

@router.post("/metrics/stream", response_model=MetricsStreamResponse)
async def stream_metrics(item: MetricsStreamItem, user=Depends(get_current_user)):
    async with async_session() as session:
        # ensure run exists
        run = await session.get(Run, item.run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        await session.execute(insert(Metric).values(run_id=item.run_id, timestamp=item.timestamp, value=item.value))
        await session.commit()
    return MetricsStreamResponse(status="accepted")


@router.get("/runs/{run_id}/metrics")
async def get_run_metrics(run_id: int, limit: int = 5000, user=Depends(get_current_user)):
    limit = min(max(limit, 1), 20000)
    async with async_session() as session:
        run = await session.get(Run, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        res = await session.execute(
            select(Metric).where(Metric.run_id == run_id).order_by(Metric.timestamp.asc()).limit(limit)
        )
        rows = res.scalars().all()
        return {
            "run_id": run_id,
            "metrics": [{"timestamp": m.timestamp.isoformat(), "value": m.value} for m in rows],
        }
