 import streamlit as st
import pandas as pd
from datetime import date
import os
import plotly.express as px

st.set_page_config(page_title="Finance Tracker")

DATA_FILE = "data.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["type","amount","category","note","date"])
    df.to_csv(DATA_FILE,index=False)

df = pd.read_csv(DATA_FILE)

st.title("💰 Personal Finance Tracker")

tab1, tab2 = st.tabs(["Add Entry","Monthly Report"])

with tab1:
    t = st.radio("Type",["Income","Expense"])
    amount = st.number_input("Amount",min_value=0.0)
    category = st.selectbox("Category",["Salary","Food","Travel","Shopping","Bills","Other"])
    note = st.text_input("Note")
    d = st.date_input("Date",date.today())

    if st.button("Save"):
        new = pd.DataFrame([[t,amount,category,note,str(d)]],
        columns=df.columns)
        df = pd.concat([df,new])
        df.to_csv(DATA_FILE,index=False)
        st.success("Saved")

with tab2:
    if not df.empty:
        df["date"]=pd.to_datetime(df["date"])
        month=st.selectbox("Month",df["date"].dt.strftime("%Y-%m").unique())

        m=df[df["date"].dt.strftime("%Y-%m")==month]

        income=m[m["type"]=="Income"]["amount"].sum()
        expense=m[m["type"]=="Expense"]["amount"].sum()

        st.metric("Income",income)
        st.metric("Expense",expense)
        st.metric("Balance",income-expense)

        st.dataframe(m)

        exp=m[m["type"]=="Expense"]
        if not exp.empty:
            fig=px.pie(exp,values="amount",names="category")
            st.plotly_chart(fig)
    else:
        st.info("No data yet") 
