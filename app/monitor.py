import httpx
import time
from sqlalchemy.orm import Session
from app.models import APIEndpoint, APILog
from app.redis_client import set_latest_status

async def check_api_endpoint(endpoint_id: int, url: str, db: Session):
    start_time = time.time()
    status = "DOWN"
    status_code = 0
    
    try:
        async with httpx.AsyncClient() as client:
            # Timeout after 5 seconds
            response = await client.get(url, timeout=5.0)
            status_code = response.status_code
            if 200 <= status_code < 400:
                status = "UP"
    except Exception as e:
        status = "DOWN"
        
    response_time = (time.time() - start_time) * 1000 # Convert to ms

    # Save to Database
    log = APILog(
        endpoint_id=endpoint_id, 
        status_code=status_code, 
        response_time_ms=response_time, 
        status=status
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    # Save to Redis Cache
    cache_data = {
        "status": status,
        "status_code": status_code,
        "response_time_ms": round(response_time, 2),
        "last_checked": log.checked_at.isoformat()
    }
    set_latest_status(endpoint_id, cache_data)
    
    return cache_data