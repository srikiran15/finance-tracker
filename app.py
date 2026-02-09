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

tab1, tab2, tab3 = st.tabs(["➕ Add Entry","📊 Monthly Report","🛠 Manage Entries"])

# ---------- ADD ENTRY ----------
with tab1:
    st.subheader("Add Income / Expense")

    t = st.radio("Type",["Income","Expense"])
    amount = st.number_input("Amount",min_value=0.0)

    category = st.selectbox("Category",["Salary","Food","Travel","Shopping","Bills","Other"], key="add_cat")

    note = st.text_input("Note")
    d = st.date_input("Date",date.today())

    if st.button("Save"):
        new = pd.DataFrame([[t,amount,category,note,str(d)]],columns=df.columns)
        df = pd.concat([df,new],ignore_index=True)
        df.to_csv(DATA_FILE,index=False)
        st.success("Saved")

# ---------- MONTHLY REPORT ----------
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

# ---------- MANAGE ENTRIES ----------
with tab3:
    st.subheader("Edit / Delete Entries")

    if not df.empty:
        df["id"]=df.index

        selected = st.selectbox("Select Entry ID",df["id"])

        row = df.loc[selected]

        etype = st.selectbox("Type",["Income","Expense"],index=0 if row["type"]=="Income" else 1)
        eamount = st.number_input("Amount",value=float(row["amount"]))

        ecat = st.selectbox("Category",["Salary","Food","Travel","Shopping","Bills","Other"], key="edit_cat")

        enote = st.text_input("Note",value=row["note"])
        edate = st.date_input("Date",pd.to_datetime(row["date"]))

        col1,col2 = st.columns(2)

        if col1.button("Update"):
            df.loc[selected] = [etype,eamount,ecat,enote,str(edate),selected]
            df.drop(columns=["id"],inplace=True)
            df.to_csv(DATA_FILE,index=False)
            st.success("Updated")

        if col2.button("Delete"):
            df=df.drop(selected)
            df.drop(columns=["id"],inplace=True)
            df.to_csv(DATA_FILE,index=False)
            st.warning("Deleted")

        st.dataframe(df.drop(columns=["id"]))
    else:
        st.info("No records")
