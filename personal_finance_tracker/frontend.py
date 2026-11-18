import streamlit as st
import requests
import pandas as pd
import datetime

st.set_page_config(page_title="Personal Finance Tracker", page_icon="💼", layout="wide")
st.title("💼 Personal Finance Tracker")
st.markdown("Track income and expenses, and show spending and savings insights.")

# URL of the FastAPI Backend
API_URL = "http://127.0.0.1:8000"

# =============================================================================
# SIDEBAR: ADD TRANSACTION (CRUD - Create)
# =============================================================================
with st.sidebar:
    st.header("➕ Add Transaction")
    with st.form("add_tx_form"):
        tx_type = st.selectbox("Type", ["Expense", "Income"])
        amount = st.number_input("Amount ($)", min_value=0.01, step=1.0)
        category = st.selectbox("Category", ["Food", "Rent", "Salary", "Entertainment", "Utilities", "Other"])
        description = st.text_input("Description", placeholder="e.g., Grocery shopping")
        tx_date = st.date_input("Date", datetime.date.today())
        
        submit_btn = st.form_submit_button("Save Transaction")
        
        if submit_btn:
            payload = {
                "amount": amount,
                "category": category,
                "description": description,
                "transaction_type": tx_type,
                "transaction_date": tx_date.strftime("%Y-%m-%d")
            }
            try:
                res = requests.post(f"{API_URL}/transactions/", json=payload)
                if res.status_code == 200:
                    st.success("Transaction saved!")
                    st.rerun()
            except Exception as e:
                st.error("Backend not running. Start backend.py first.")

# =============================================================================
# MAIN DASHBOARD: FETCH DATA & ANALYZE
# =============================================================================
try:
    # Fetch data from FastAPI
    response = requests.get(f"{API_URL}/transactions/")
    transactions = response.json()
    
    if not transactions:
        st.info("No transactions yet. Add one in the sidebar!")
    else:
        # Convert to Pandas DataFrame for analysis
        df = pd.DataFrame(transactions)
        
        # Calculate Metrics
        total_income = df[df["transaction_type"] == "Income"]["amount"].sum()
        total_expense = df[df["transaction_type"] == "Expense"]["amount"].sum()
        balance = total_income - total_expense
        
        # --- TOP METRICS ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Balance", f"${balance:,.2f}")
        col2.metric("Total Income", f"${total_income:,.2f}")
        col3.metric("Total Expenses", f"${total_expense:,.2f}")
        
        st.divider()
        
        # --- DATA ANALYTICS (Charts) ---
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("📊 Spending by Category")
            expenses_df = df[df["transaction_type"] == "Expense"]
            if not expenses_df.empty:
                # Group by category for pie chart
                category_totals = expenses_df.groupby("category")["amount"].sum()
                st.bar_chart(category_totals)
            else:
                st.write("No expenses to show.")
                
        with col_chart2:
            st.subheader("📈 Daily Spending Trend")
            # Group by date for line chart
            daily_spending = expenses_df.groupby("transaction_date")["amount"].sum().reset_index()
            if not daily_spending.empty:
                st.line_chart(data=daily_spending, x="transaction_date", y="amount")
            else:
                st.write("No expenses to show.")
        
        st.divider()
        
        # --- RECENT TRANSACTIONS TABLE (CRUD - Read & Delete) ---
        st.subheader("📋 Recent Transactions")
        
        # Display table
        st.dataframe(df[["id", "transaction_date", "transaction_type", "category", "description", "amount"]], use_container_width=True, hide_index=True)
        
        # Delete functionality
        st.subheader("🗑️ Delete a Transaction")
        delete_id = st.selectbox("Select Transaction ID to delete", df["id"].tolist())
        if st.button("Delete Transaction", type="primary"):
            requests.delete(f"{API_URL}/transactions/{delete_id}")
            st.success(f"Deleted transaction {delete_id}")
            st.rerun()

except requests.exceptions.ConnectionError:
    st.error("⚠️ Cannot connect to the backend. Make sure `backend.py` is running.")