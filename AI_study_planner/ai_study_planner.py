import streamlit as st
import datetime
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker
import threading
import uvicorn
import time

# =============================================================================
# 1. BACKEND: FASTAPI & SQLITE DATABASE
# =============================================================================

# Database Setup (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./study_planner.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
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

# FastAPI App & Pydantic Models
app = FastAPI()

class GoalCreate(BaseModel):
    subject: str
    target_hours: float
    deadline: str # YYYY-MM-DD
    priority: str

# CRUD Operations
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/goals/")
def create_goal(goal: GoalCreate):
    db = SessionLocal()
    db_goal = GoalDB(**goal.dict())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    
    # --- SCHEDULING LOGIC ---
    # Calculate how many days are left until the deadline
    today = datetime.date.today()
    deadline_date = datetime.datetime.strptime(goal.deadline, "%Y-%m-%d").date()
    days_left = (deadline_date - today).days
    
    if days_left <= 0:
        days_left = 1 # Prevent division by zero
        
    # Simple logic: spread hours evenly across days left
    hours_per_day = goal.target_hours / days_left
    
    # Create schedule entries for the next X days
    for i in range(min(days_left, 14)): # Schedule up to 14 days ahead
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
    return {"message": "Goal created and scheduled!", "goal_id": db_goal.id}

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

# Run FastAPI in a background thread so Streamlit can run in the main thread
def run_backend():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

if "backend_running" not in st.session_state:
    thread = threading.Thread(target=run_backend, daemon=True)
    thread.start()
    st.session_state["backend_running"] = True
    time.sleep(2) # Give the server a moment to start

# =============================================================================
# 2. FRONTEND: STREAMLIT UI
# =============================================================================

st.set_page_config(page_title="AI Study Planner", page_icon="📅", layout="wide")
st.title("📅 AI Study Planner")
st.markdown("Creates a personalized study plan based on goals, available time, and progress.")

# Sidebar for adding new goals
with st.sidebar:
    st.header("🎯 Add a New Goal")
    with st.form("goal_form"):
        subject = st.text_input("Subject / Topic", placeholder="e.g., FastAPI Backend")
        target_hours = st.number_input("Total Hours Needed", min_value=0.5, step=0.5, value=10.0)
        deadline = st.date_input("Deadline", min_value=datetime.date.today())
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        submit_btn = st.form_submit_button("Generate Plan")
        
        if submit_btn and subject:
            payload = {
                "subject": subject,
                "target_hours": target_hours,
                "deadline": deadline.strftime("%Y-%m-%d"),
                "priority": priority
            }
            # Send to FastAPI backend
            try:
                res = requests.post("http://127.0.0.1:8000/goals/", json=payload)
                if res.status_code == 200:
                    st.success(f"Added plan for {subject}!")
                    st.rerun() # Refresh to show new data
                else:
                    st.error("Error creating goal.")
            except Exception as e:
                st.error(f"Backend connection error: {e}")

# Main Layout - Tabs for Goals and Schedule
tab1, tab2 = st.tabs(["📚 My Goals", "🗓️ Study Schedule"])

with tab1:
    st.subheader("Current Goals")
    try:
        goals_data = requests.get("http://127.0.0.1:8000/goals/").json()
        if not goals_data:
            st.info("No goals yet. Add one in the sidebar!")
        else:
            for g in goals_data:
                with st.expander(f"**{g['subject']}** (Priority: {g['priority']})"):
                    st.write(f"🎯 **Target:** {g['target_hours']} hours")
                    st.write(f"📅 **Deadline:** {g['deadline']}")
    except:
        st.error("Could not connect to backend.")

with tab2:
    st.subheader("Your Auto-Generated Schedule")
    try:
        schedule_data = requests.get("http://127.0.0.1:8000/schedule/").json()
        if not schedule_data:
            st.info("Schedule is empty. Add a goal to generate a plan.")
        else:
            # Organize by date
            dates = sorted(list(set([s['study_date'] for s in schedule_data])))
            
            for date in dates:
                st.markdown(f"### 📆 {date}")
                daily_tasks = [s for s in schedule_data if s['study_date'] == date]
                
                for task in daily_tasks:
                    # Format as a nice UI card
                    st.info(f"**{task['subject']}** — ⏱️ Study for **{task['hours']} hours**")
    except:
        st.error("Could not connect to backend.")