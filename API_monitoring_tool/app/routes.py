from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import APIEndpoint, APILog
from app.schemas import EndpointCreate, EndpointResponse, LogResponse
from app.monitor import check_api_endpoint
from app.redis_client import get_latest_status

router = APIRouter()

@router.post("/endpoints/", response_model=EndpointResponse)
def create_endpoint(endpoint: EndpointCreate, db: Session = Depends(get_db)):
    db_endpoint = db.query(APIEndpoint).filter(APIEndpoint.url == endpoint.url).first()
    if db_endpoint:
        raise HTTPException(status_code=400, detail="Endpoint already exists")
    
    new_endpoint = APIEndpoint(name=endpoint.name, url=endpoint.url)
    db.add(new_endpoint)
    db.commit()
    db.refresh(new_endpoint)
    return new_endpoint

@router.post("/endpoints/{endpoint_id}/check")
async def trigger_check(endpoint_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    endpoint = db.query(APIEndpoint).filter(APIEndpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    # Run check in background so it doesn't block the API
    background_tasks.add_task(check_api_endpoint, endpoint.id, endpoint.url, db)
    return {"message": "Check started in the background"}

@router.get("/endpoints/{endpoint_id}/status")
def get_status(endpoint_id: int):
    # First try Redis
    cached_data = get_latest_status(endpoint_id)
    if cached_data:
        return {"source": "Redis Cache", "data": cached_data}
    
    # If not in Redis, tell user to trigger a check
    return {"source": "None", "message": "No cached status. Trigger a check first."}

@router.get("/endpoints/{endpoint_id}/logs", response_model=List[LogResponse])
def get_logs(endpoint_id: int, limit: int = 10, db: Session = Depends(get_db)):
    logs = db.query(APILog).filter(APILog.endpoint_id == endpoint_id).order_by(APILog.checked_at.desc()).limit(limit).all()
    return logs