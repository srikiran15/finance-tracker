import streamlit as st
import pandas as pd
import os
from datetime import date
import matplotlib.pyplot as plt

FILE = "data.csv"
PIN = "1234"

st.set_page_config(page_title="Finance Tracker", layout="wide")

# ---------- PIN LOCK ----------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    p = st.text_input("Enter 4 Digit PIN", type="password")
    if p == PIN:
        st.session_state.auth = True
        st.rerun()
    st.stop()

# ---------- LOAD DATA ----------
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["date","type","category","amount","note"])

df["date"] = pd.to_datetime(df["date"])

# ---------- SIDEBAR ----------
page = st.sidebar.radio("Menu",["Add Entry","Dashboard","Edit/Delete"])

# ---------- ADD ENTRY ----------
if page=="Add Entry":

    st.header("➕ Add Entry")

    d = st.date_input("Date",date.today())
    t = st.selectbox("Type",["Income","Expense"])
    c = st.selectbox("Category",["Salary","Food","Travel","Shopping","Bills","Other"])
    a = st.number_input("Amount",min_value=0.0)
    n = st.text_input("Note")

    if st.button("Submit"):

        new = pd.DataFrame([[d,t,c,a,n]],columns=df.columns)
        df = pd.concat([df,new],ignore_index=True)
        df.to_csv(FILE,index=False)

        st.success("Saved!")
        st.rerun()

# ---------- DASHBOARD ----------
elif page=="Dashboard":

    st.header("📊 Dashboard")

    month = st.selectbox("Select Month",sorted(df["date"].dt.to_period("M").astype(str).unique()))

    m = df[df["date"].dt.to_period("M").astype(str)==month]

    month_income = m[m["type"]=="Income"]["amount"].sum()
    month_expense = m[m["type"]=="Expense"]["amount"].sum()

    total_income = df[df["type"]=="Income"]["amount"].sum()
    total_expense = df[df["type"]=="Expense"]["amount"].sum()

    overall = total_income-total_expense

    st.markdown(f"### 🟢 Month Income: +₹{month_income}")
    st.markdown(f"### 🔴 Month Expense: -₹{month_expense}")
    st.markdown("---")
    st.markdown(f"## 💼 Overall Balance: ₹{overall}")

    # ---------- DAILY BALANCE ----------
    ddf=df.sort_values("date")
    ddf["signed"]=ddf.apply(lambda x: x["amount"] if x["type"]=="Income" else -x["amount"],axis=1)
    ddf["balance"]=ddf["signed"].cumsum()

    st.subheader("📈 Balance Over Time")
    st.line_chart(ddf.set_index("date")["balance"])

    # ---------- PIE CHARTS ----------
    st.subheader("🧁 Category Pie")

    fig,ax=plt.subplots(1,2)

    inc=m[m["type"]=="Income"].groupby("category")["amount"].sum()
    exp=m[m["type"]=="Expense"].groupby("category")["amount"].sum()

    if not inc.empty:
        ax[0].pie(inc,labels=inc.index,autopct="%1.0f%%")
        ax[0].set_title("Income")

    if not exp.empty:
        ax[1].pie(exp,labels=exp.index,autopct="%1.0f%%")
        ax[1].set_title("Expense")

    st.pyplot(fig)

    # ---------- CATEGORY SUMMARY ----------
    st.subheader("📋 Monthly Category Summary")
    st.dataframe(exp.reset_index())

    # ---------- DOWNLOAD ----------
    st.download_button("⬇ Download CSV",df.to_csv(index=False),"finance.csv")

# ---------- EDIT DELETE ----------
else:

    st.header("✏ Edit / Delete")

    for i,row in df.iterrows():

        with st.expander(f"{row['date'].date()} {row['category']} ₹{row['amount']}"):

            d=st.date_input("Date",row["date"],key=f"d{i}")
            t=st.selectbox("Type",["Income","Expense"],index=0 if row["type"]=="Income" else 1,key=f"t{i}")
            c=st.selectbox("Category",["Salary","Food","Travel","Shopping","Bills","Other"],key=f"c{i}")
            a=st.number_input("Amount",value=row["amount"],key=f"a{i}")
            n=st.text_input("Note",row["note"],key=f"n{i}")

            if st.button("Update",key=f"u{i}"):
                df.loc[i]=[d,t,c,a,n]
                df.to_csv(FILE,index=False)
                st.rerun()

            if st.button("Delete",key=f"x{i}"):
                df=df.drop(i)
                df.to_csv(FILE,index=False)
                st.rerun()
