from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class MetricPoint(BaseModel):
    timestamp: datetime
    value: float = Field(..., ge=-1e12, le=1e12)


class MetricsUpload(BaseModel):
    run_name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)
    metrics: List[MetricPoint] = Field(min_length=1)


class MetricsStreamItem(BaseModel):
    run_id: int
    timestamp: datetime
    value: float = Field(..., ge=-1e12, le=1e12)


class MetricsStreamResponse(BaseModel):
    status: str
