import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

st.set_page_config(layout="wide")

FILE="data.csv"

if not os.path.exists(FILE):
    pd.DataFrame(columns=["date","type","category","description","amount"]).to_csv(FILE,index=False)

df=pd.read_csv(FILE)
df["date"]=pd.to_datetime(df["date"],errors="coerce")

page=st.sidebar.radio("Menu",["➕ Add","📊 Report","🗑 Delete"])

# ---------------- ADD ----------------
if page=="➕ Add":

    st.title("➕ Add Entry")

    with st.form("add",clear_on_submit=True):

        d=st.date_input("Date",date.today())
        t=st.selectbox("Type",["Income","Expense"])
        c=st.selectbox("Category",["Salary","Food","Travel","Shopping","Bills","Other"])
        desc=st.text_input("Description")
        a=st.number_input("Amount",min_value=0.0)

        if st.form_submit_button("Save"):
            df.loc[len(df)]=[d,t,c,desc,a]
            df.to_csv(FILE,index=False)
            st.success("Saved")

# ---------------- REPORT ----------------
elif page=="📊 Report":

    st.title("📊 Monthly Report")

    df["month"]=df["date"].dt.to_period("M").astype(str)

    msel=st.selectbox("Month",sorted(df["month"].dropna().unique(),reverse=True))
    m=df[df["month"]==msel]

    minc=m[m.type=="Income"]["amount"].sum()
    mexp=m[m.type=="Expense"]["amount"].sum()

    tinc=df[df.type=="Income"]["amount"].sum()
    texp=df[df.type=="Expense"]["amount"].sum()

    bal=tinc-texp

    st.markdown(f"### 🟢 Month Income: +₹{minc}")
    st.markdown(f"### 🔴 Month Expense: -₹{mexp}")
    st.markdown("---")
    st.markdown(f"## 💼 Overall Balance: ₹{bal}")

    show=m.copy()
    show["Amount"]=show.apply(lambda r:f"+{r.amount}" if r.type=="Income" else f"-{r.amount}",axis=1)

    st.dataframe(show[["date","type","category","description","Amount"]],use_container_width=True)

    if not m.empty:
        fig=px.pie(m[m.type=="Expense"],names="category",values="amount")
        st.plotly_chart(fig,use_container_width=True)

# ---------------- DELETE ----------------
else:

    st.title("🗑 Delete Entry")

    df["label"]=df.apply(lambda r:f"{r.date.date()} | {r.description} | ₹{r.amount}",axis=1)

    choice=st.selectbox("Select entry",df["label"])

    if st.button("Delete"):
        df=df[df["label"]!=choice]
        df.drop(columns="label",inplace=True)
        df.to_csv(FILE,index=False)
        st.success("Deleted")
        st.experimental_rerun()
