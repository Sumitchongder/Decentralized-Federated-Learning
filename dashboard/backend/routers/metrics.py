from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Pydantic model for metric payload
class Metric(BaseModel):
    round: int
    cid: str
    accuracy: float = None

metrics_storage: List[Metric] = []

@router.post("/")
async def post_metric(metric: Metric):
    metrics_storage.append(metric)
    return {"status": "ok"}

@router.get("/")
async def get_metrics():
    return metrics_storage
