import streamlit as st
import pandas as pd
from datetime import datetime
from google import genai

# 🔑 Paste your Gemini API key here
client = genai.Client(api_key="API")

# 🎨 Page Config
st.set_page_config(page_title="AI Expense Tracker", layout="wide")

st.markdown("""
<style>
.main {
    background-color: #0f172a;
    color: white;
}
.stButton>button {
    background-color: #22c55e;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.title("💰 AI Smart Expense Dashboard")

# ---------------- LOGIN ----------------
st.sidebar.title("🔐 Login")
username = st.sidebar.text_input("Enter your name")

if not username:
    st.warning("Please enter your name to continue")
    st.stop()

st.success(f"Welcome {username} 👋")

# ---------------- ADD EXPENSE ----------------
st.sidebar.header("➕ Add Expense")

amount = st.sidebar.number_input("Amount", min_value=0)
category = st.sidebar.selectbox("Category", ["Food", "Travel", "Shopping", "Bills"])
date = st.sidebar.date_input("Date", datetime.today())

if st.sidebar.button("Add Expense"):
    new_data = pd.DataFrame({
        "User": [username],
        "Amount": [amount],
        "Category": [category],
        "Date": [date]
    })

    try:
        old_data = pd.read_csv("expenses.csv")
        df = pd.concat([old_data, new_data], ignore_index=True)
    except:
        df = new_data

    df.to_csv("expenses.csv", index=False)
    st.success("Expense Added!")

# ---------------- LOAD DATA ----------------
try:
    df = pd.read_csv("expenses.csv")
    df = df[df["User"] == username]
except:
    df = pd.DataFrame(columns=["User","Amount","Category","Date"])

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)

total = df["Amount"].sum() if not df.empty else 0
avg = df["Amount"].mean() if not df.empty else 0

with col1:
    st.metric("💰 Total Spending", int(total))

with col2:
    st.metric("📊 Average Spending", int(avg) if not pd.isna(avg) else 0)

with col3:
    budget = st.number_input("💸 Set Monthly Budget", value=5000)

# ---------------- BUDGET ALERT ----------------
if total > budget:
    st.error("⚠️ Budget Exceeded!")
elif total > 0.8 * budget:
    st.warning("⚡ You are close to budget limit")
else:
    st.success("✅ Budget under control")

# ---------------- CATEGORY CHART ----------------
st.subheader("📂 Category Breakdown")

if not df.empty:
    cat = df.groupby("Category")["Amount"].sum()
    st.bar_chart(cat)

# ---------------- TREND CHART ----------------
st.subheader("📈 Spending Trend")

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])
    trend = df.groupby("Date")["Amount"].sum()
    st.line_chart(trend)

# ---------------- AI INSIGHT ----------------
st.subheader("🧠 AI Financial Advisor")

if st.button("Analyze My Spending"):
    prompt = f"""
    User spent ₹{total}.
    Give:
    1. Spending habit insight
    2. Saving tips
    3. Where to reduce cost
    """

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    st.write(response.text)
