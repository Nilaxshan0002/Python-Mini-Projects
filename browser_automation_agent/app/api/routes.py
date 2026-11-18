from fastapi import APIRouter, HTTPException
from app.models.schemas import TaskRequest, TaskResponse
from app.agent.loop import run_agent_task
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Notice: "async def" is changed to "def"
@router.post("/run-task", response_model=TaskResponse)
def run_task(request: TaskRequest):
    """
    Endpoint to trigger the browser automation agent.
    Runs in a separate thread to prevent blocking the main server loop.
    """
    try:
        logger.info(f"Received task: {request.task}")
        
        # Run the agent
        result_summary, steps = run_agent_task(
            task=request.task, 
            start_url=request.start_url
        )
        
        return TaskResponse(
            status="success", 
            result=result_summary,
            steps_taken=steps
        )
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check():
    return {"status": "healthy", "message": "AutoBrowse Agent API is running."}