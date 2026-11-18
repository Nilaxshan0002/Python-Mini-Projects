from pydantic import BaseModel, Field

class TaskRequest(BaseModel):
    task: str = Field(..., description="The instruction for the AI agent to perform.")
    start_url: str = Field(default="https://www.google.com", description="The URL to start the task on.")

class TaskResponse(BaseModel):
    status: str = Field(..., description="Status of the task (success/failed).")
    result: str = Field(..., description="The final output or summary from the agent.")
    steps_taken: int = Field(default=0, description="Number of actions the agent took.")