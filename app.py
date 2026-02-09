import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

st.set_page_config(layout="wide")

FILE = "data.csv"

# ---------------- INIT DATA ----------------
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["date","type","category","description","amount"])
    df.to_csv(FILE,index=False)

df = pd.read_csv(FILE)
df["date"] = pd.to_datetime(df["date"])

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio("Menu",["➕ Add Entry","📊 Monthly Report","🗂 Edit / Delete"])

# ---------------- ADD ENTRY ----------------
if page=="➕ Add Entry":

    st.title("➕ Add Transaction")

    with st.form("add",clear_on_submit=True):

        tdate = st.date_input("Date",date.today())
        ttype = st.selectbox("Type",["Income","Expense"])
        cat = st.selectbox("Category",["Salary","Food","Travel","Shopping","Bills","Other"])
        desc = st.text_input("Description")
        amt = st.number_input("Amount",min_value=0.0,step=1.0)

        submit = st.form_submit_button("Save")

    if submit:
        df.loc[len(df)] = [tdate,ttype,cat,desc,amt]
        df.to_csv(FILE,index=False)
        st.success("Saved!")

# ---------------- MONTHLY REPORT ----------------
elif page=="📊 Monthly Report":

    st.title("📊 Monthly Report")

    df["month"] = df["date"].dt.to_period("M").astype(str)
    month = st.selectbox("Select Month",sorted(df["month"].unique(),reverse=True))

    m = df[df["month"]==month]

    month_income = m[m["type"]=="Income"]["amount"].sum()
    month_expense = m[m["type"]=="Expense"]["amount"].sum()

    total_income = df[df["type"]=="Income"]["amount"].sum()
    total_expense = df[df["type"]=="Expense"]["amount"].sum()

    overall_balance = total_income-total_expense

    col1,col2,col3 = st.columns(3)

    col1.markdown(f"### 🟢 Month Income\n## +₹{month_income}")
    col2.markdown(f"### 🔴 Month Expense\n## -₹{month_expense}")
    col3.markdown(f"### 💼 Overall Balance\n## ₹{overall_balance}")

    st.markdown("---")

    # Coloring rows
    display = m.copy()
    display["Signed Amount"] = display.apply(
        lambda r: f"+{r['amount']}" if r["type"]=="Income" else f"-{r['amount']}",axis=1)

    st.dataframe(display[["date","type","category","description","Signed Amount"]],use_container_width=True)

    if not m.empty:
        pie = px.pie(m[m["type"]=="Expense"],names="category",values="amount",title="Expense Breakdown")
        st.plotly_chart(pie,use_container_width=True)

# ---------------- EDIT DELETE ----------------
elif page=="🗂 Edit / Delete":

    st.title("🗂 Edit / Delete")

    for i,row in df.iterrows():

        with st.expander(f"{row['date'].date()} | {row['description']} | ₹{row['amount']}"):

            edate = st.date_input("Date",row["date"],key=f"d{i}")
            etype = st.selectbox("Type",["Income","Expense"],index=0 if row["type"]=="Income" else 1,key=f"t{i}")
            ecat = st.selectbox("Category",["Salary","Food","Travel","Shopping","Bills","Other"],key=f"c{i}")
            edesc = st.text_input("Description",row["description"],key=f"s{i}")
            eamt = st.number_input("Amount",value=float(row["amount"]),key=f"a{i}")

            col1,col2 = st.columns(2)

            if col1.button("Update",key=f"u{i}"):

                df.loc[i]=[edate,etype,ecat,edesc,eamt]
                df.to_csv(FILE,index=False)
                st.experimental_rerun()

            if col2.button("Delete",key=f"x{i}"):

                df=df.drop(i).reset_index(drop=True)
                df.to_csv(FILE,index=False)
                st.experimental_rerun()
