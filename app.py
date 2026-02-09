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

# ---------------- ADD ENTRY ----------------
with tab1:
    t = st.radio("Type",["Income","Expense"], key="add_type")
    amount = st.number_input("Amount",min_value=0.0, key="add_amount")
    category = st.selectbox("Category",["Salary","Food","Travel","Shopping","Bills","Other"], key="add_cat")
    note = st.text_input("Note", key="add_note")
    d = st.date_input("Date",date.today(), key="add_date")

    if st.button("Save", key="add_save"):
        new = pd.DataFrame([[t,amount,category,note,str(d)]],columns=df.columns)
        df = pd.concat([df,new],ignore_index=True)
        df.to_csv(DATA_FILE,index=False)
        st.success("Saved")

# ---------------- MONTHLY REPORT ----------------
with tab2:
    if not df.empty:
        df["date"]=pd.to_datetime(df["date"])
        month=st.selectbox("Month",df["date"].dt.strftime("%Y-%m").unique(), key="rep_month")

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

# ---------------- MANAGE ENTRIES ----------------
with tab3:
    if not df.empty:
        df["id"]=df.index

        selected = st.selectbox("Select Entry ID",df["id"], key="edit_id")

        row = df.loc[selected]

        etype = st.selectbox("Edit Type",["Income","Expense"],
                             index=0 if row["type"]=="Income" else 1,
                             key="edit_type")

        eamount = st.number_input("Edit Amount",value=float(row["amount"]), key="edit_amount")

        ecat = st.selectbox("Edit Category",["Salary","Food","Travel","Shopping","Bills","Other"], key="edit_cat")

        enote = st.text_input("Edit Note",value=row["note"], key="edit_note")

        edate = st.date_input("Edit Date",pd.to_datetime(row["date"]), key="edit_date")

        col1,col2 = st.columns(2)

        if col1.button("Update", key="update_btn"):
            df.loc[selected] = [etype,eamount,ecat,enote,str(edate),selected]
            df.drop(columns=["id"],inplace=True)
            df.to_csv(DATA_FILE,index=False)
            st.success("Updated")

        if col2.button("Delete", key="delete_btn"):
            df=df.drop(selected)
            df.drop(columns=["id"],inplace=True)
            df.to_csv(DATA_FILE,index=False)
            st.warning("Deleted")

        st.dataframe(df.drop(columns=["id"]))
    else:
        st.info("No records")
