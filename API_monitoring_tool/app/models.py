from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class APIEndpoint(Base):
    __tablename__ = "endpoints"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to logs
    logs = relationship("APILog", back_populates="endpoint")

class APILog(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id"))
    status_code = Column(Integer)
    response_time_ms = Column(Float)
    status = Column(String) # "UP" or "DOWN"
    checked_at = Column(DateTime, default=datetime.utcnow)

    endpoint = relationship("APIEndpoint", back_populates="logs")