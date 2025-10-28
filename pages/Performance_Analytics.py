import streamlit as st
import pandas as pd
import numpy as np


if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Please log in to access this page.")
    st.stop()


st.set_page_config(page_title="Performance Analytics", layout="wide")

st.markdown("<div class='card'><h3> Performance Analytics</h3></div>", unsafe_allow_html=True)

# Simulated performance data
products = [f"Product {i}" for i in range(1, 8)]
sales = np.random.randint(100, 1000, 7)
profits = np.random.randint(10, 200, 7)
df = pd.DataFrame({"Product": products, "Sales": sales, "Profit": profits})

col1, col2 = st.columns(2)
with col1:
    st.bar_chart(df.set_index("Product")["Sales"])
with col2:
    st.bar_chart(df.set_index("Product")["Profit"])

# Performance insights
best = df.loc[df["Sales"].idxmax(), "Product"]
worst = df.loc[df["Sales"].idxmin(), "Product"]
st.markdown(
    f"""
    <div class='card'>
      <strong> Insights</strong>
      <p>Top performing product: <b>{best}</b></p>
      <p>Lowest performing product: <b>{worst}</b></p>
      <p style='color:#475569;'>Use these insights to balance your inventory and optimize restocking strategy.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
