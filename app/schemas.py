from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List

class EndpointCreate(BaseModel):
    name: str
    url: str

class EndpointResponse(BaseModel):
    id: int
    name: str
    url: str
    class Config:
        from_attributes = True

class LogResponse(BaseModel):
    status_code: int
    response_time_ms: float
    status: str
    checked_at: datetime
    class Config:
        from_attributes = True