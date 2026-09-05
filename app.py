import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Superstore Sales & Profitability", layout="wide")

# ---- Load data ----
@st.cache_data
def load_data():
    df = pd.read_csv("superstore_clean.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

df = load_data()

st.title("Retail Sales & Profitability Dashboard")
st.caption("Superstore dataset — filter below to explore sales, profit, and discount patterns.")

# ---- Sidebar filters ----
st.sidebar.header("Filters")

region_options = ["All"] + sorted(df["Region"].unique().tolist())
selected_region = st.sidebar.selectbox("Region", region_options)

category_options = ["All"] + sorted(df["Category"].unique().tolist())
selected_category = st.sidebar.selectbox("Category", category_options)

filtered = df.copy()
if selected_region != "All":
    filtered = filtered[filtered["Region"] == selected_region]
if selected_category != "All":
    filtered = filtered[filtered["Category"] == selected_category]

# ---- KPI row ----
total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
margin = (total_profit / total_sales * 100) if total_sales else 0
order_count = filtered.shape[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"₹{total_sales:,.0f}")
col2.metric("Total Profit", f"₹{total_profit:,.0f}")
col3.metric("Profit Margin", f"{margin:.1f}%")
col4.metric("Orders", f"{order_count:,}")

st.divider()

# ---- Charts ----
left, right = st.columns(2)

with left:
    st.subheader("Profit by Sub-Category")
    sub_profit = filtered.groupby("Sub-Category")["Profit"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(6, 5))
    colors = ["#d62728" if v < 0 else "#4C72B0" for v in sub_profit]
    ax.barh(sub_profit.index, sub_profit.values, color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Total Profit (₹)")
    st.pyplot(fig)

with right:
    st.subheader("Avg Profit Margin by Discount Band")
    temp = filtered.copy()
    temp["Discount Band"] = pd.cut(
        temp["Discount"], bins=[-0.01, 0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=["0%", "1-20%", "21-40%", "41-60%", "61-80%", "81-100%"]
    )
    band_margin = temp.groupby("Discount Band", observed=True)["Profit Margin"].mean() * 100
    fig2, ax2 = plt.subplots(figsize=(6, 5))
    colors2 = ["#2ca02c" if v >= 0 else "#d62728" for v in band_margin]
    ax2.bar(band_margin.index.astype(str), band_margin.values, color=colors2)
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.set_ylabel("Avg Profit Margin (%)")
    st.pyplot(fig2)

st.divider()
st.subheader("Monthly Sales Trend")
monthly = filtered.groupby(filtered["Order Date"].dt.to_period("M"))["Sales"].sum()
monthly.index = monthly.index.to_timestamp()
st.line_chart(monthly)

st.divider()
with st.expander("Key takeaways"):
    st.markdown("""
    - Discounts above ~20% flip average profit margin negative, and losses grow sharply past 40% discount.
    - Tables is the biggest loss-making sub-category overall.
    - Central region trails West on profit margin despite comparable sales volume.
    """)
