from fastapi import APIRouter
from app.schemas.brute import BruteRequest
from app.services.brute_service import start_brute_force
from app.core.celery_app import celery_app
from celery.result import AsyncResult

router = APIRouter()

@router.post("/brut_hash")
def brute_hash(req: BruteRequest):
    task = start_brute_force(req.hash, req.charset, req.max_length)
    return {"task_id": task.id}

@router.get("/get_status")
def get_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "status": result.status.lower(),
        "progress": result.info.get("progress", 0) if result.info else 0,
        "result": result.result if result.successful() else None
    }
