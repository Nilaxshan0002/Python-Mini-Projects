from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

# --- Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./study_planner.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GoalDB(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    target_hours = Column(Float)
    deadline = Column(String)
    priority = Column(String)

class ScheduleDB(Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer)
    subject = Column(String)
    study_date = Column(String)
    hours = Column(Float)

Base.metadata.create_all(bind=engine)

# --- FastAPI App ---
app = FastAPI()

class GoalCreate(BaseModel):
    subject: str
    target_hours: float
    deadline: str
    priority: str

@app.post("/goals/")
def create_goal(goal: GoalCreate):
    db = SessionLocal()
    db_goal = GoalDB(**goal.dict())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)

    # Basic Scheduling Logic
    today = datetime.date.today()
    deadline_date = datetime.datetime.strptime(goal.deadline, "%Y-%m-%d").date()
    days_left = max((deadline_date - today).days, 1)
    hours_per_day = goal.target_hours / days_left

    for i in range(min(days_left, 14)):
        study_date = today + datetime.timedelta(days=i)
        db_schedule = ScheduleDB(
            goal_id=db_goal.id,
            subject=goal.subject,
            study_date=study_date.strftime("%Y-%m-%d"),
            hours=round(hours_per_day, 2)
        )
        db.add(db_schedule)

    db.commit()
    db.close()
    return {"message": "Goal created"}

@app.get("/goals/")
def get_goals():
    db = SessionLocal()
    goals = db.query(GoalDB).all()
    db.close()
    return goals

@app.get("/schedule/")
def get_schedule():
    db = SessionLocal()
    schedule = db.query(ScheduleDB).all()
    db.close()
    return schedule