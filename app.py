import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# تنظیمات صفحه
st.set_page_config(page_title="داشبورد مالی هوشمند", layout="wide")

# استایل‌دهی راست‌چین برای فارسی
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    div[data-testid="stMetricValue"] { text-align: right; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 داشبورد مدیریت مالی هوشمند")
st.sidebar.header("ثبت تراکنش جدید")

# شبیه‌سازی پایگاه داده با Session State
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["تاریخ", "نوع", "دسته بندی", "مبلغ"])

# --- فرم ورود داده در سایدبار ---
with st.sidebar.form("finance_form"):
    date = st.date_input("تاریخ", datetime.now())
    t_type = st.selectbox("نوع تراکنش", ["درآمد", "هزینه"])
    category = st.selectbox("دسته بندی", ["حقوق", "اجاره", "خوراک", "تفریح", "سرمایه‌گذاری", "سایر"])
    amount = st.number_input("مبلغ (تومان)", min_value=0, step=1000)
    submit = st.form_submit_button("ثبت تراکنش")

    if submit:
        new_data = pd.DataFrame([[date, t_type, category, amount]], 
                                columns=["تاریخ", "نوع", "دسته بندی", "مبلغ"])
        st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
        st.success("تراکنش با موفقیت ثبت شد!")

df = st.session_state.data

# --- بخش محاسبات و شاخص‌ها (KPIs) ---
if not df.empty:
    total_income = df[df["نوع"] == "درآمد"]["مبلغ"].sum()
    total_expense = df[df["نوع"] == "هزینه"]["مبلغ"].sum()
    balance = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("موجودی کل", f"{balance:,} تومان")
    col2.metric("جمع درآمد", f"{total_income:,} تومان", delta_color="normal")
    col3.metric("جمع مخارج", f"{total_expense:,} تومان", delta="-")

    st.divider()

    # --- نمودارها ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("توزیع هزینه‌ها")
        expense_df = df[df["نوع"] == "هزینه"]
        if not expense_df.empty:
            fig_pie = px.pie(expense_df, values='مبلغ', names='دسته بندی', hole=0.4,
                             color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("هنوز هزینه‌ای ثبت نشده است.")

    with col_chart2:
        st.subheader("روند تراکنش‌ها")
        if not df.empty:
            df['تاریخ'] = pd.to_datetime(df['تاریخ'])
            trend_df = df.groupby(['تاریخ', 'نوع']).sum().reset_index()
            fig_line = px.line(trend_df, x='تاریخ', y='مبلغ', color='نوع', markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

    # نمایش جدول داده‌ها
    st.subheader("📜 لیست آخرین تراکنش‌ها")
    st.dataframe(df.sort_values(by="تاریخ", ascending=False), use_container_width=True)

else:
    st.warning("لطفاً اولین تراکنش خود را از منوی سمت راست وارد کنید.")