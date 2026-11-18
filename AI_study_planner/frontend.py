import streamlit as st
import requests
import datetime

st.set_page_config(page_title="AI Study Planner", page_icon="📅", layout="wide")
st.title("📅 AI Study Planner")

# --- Sidebar ---
with st.sidebar:
    st.header("🎯 Add a New Goal")
    with st.form("goal_form"):
        subject = st.text_input("Subject", placeholder="e.g., FastAPI Backend")
        target_hours = st.number_input("Total Hours", min_value=0.5, step=0.5)
        deadline = st.date_input("Deadline", min_value=datetime.date.today())
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        submit = st.form_submit_button("Generate Plan")

        if submit and subject:
            payload = {
                "subject": subject,
                "target_hours": target_hours,
                "deadline": deadline.strftime("%Y-%m-%d"),
                "priority": priority
            }
            try:
                requests.post("http://127.0.0.1:8000/goals/", json=payload)
                st.success("Goal added!")
                st.rerun()
            except requests.exceptions.ConnectionError:
                st.error("Backend not running. Start backend.py first.")

# --- Main Tabs ---
tab1, tab2 = st.tabs(["📚 My Goals", "🗓️ Study Schedule"])

with tab1:
    st.subheader("Current Goals")
    try:
        goals = requests.get("http://127.0.0.1:8000/goals/").json()
        if not goals:
            st.info("No goals yet.")
        for g in goals:
            st.info(f"**{g['subject']}** | Target: {g['target_hours']}h | Deadline: {g['deadline']}")
    except:
        st.error("Could not connect to backend.")

with tab2:
    st.subheader("Your Auto-Generated Schedule")
    try:
        schedule = requests.get("http://127.0.0.1:8000/schedule/").json()
        if not schedule:
            st.info("Schedule is empty. Add a goal to generate a plan.")
        else:
            dates = sorted(set(s['study_date'] for s in schedule))
            for date in dates:
                st.markdown(f"**{date}**")
                for task in [s for s in schedule if s['study_date'] == date]:
                    st.success(f"📖 {task['subject']} — ⏱️ {task['hours']} hours")
    except:
        st.error("Could not connect to backend.")