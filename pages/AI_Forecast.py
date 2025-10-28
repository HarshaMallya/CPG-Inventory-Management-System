import streamlit as st
import pandas as pd
import numpy as np

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Please log in to access this page.")
    st.stop()

st.set_page_config(page_title="AI Forecast", layout="wide")

st.markdown("<div class='card'><h3>🤖 AI Forecast</h3></div>", unsafe_allow_html=True)

# Placeholder forecast data (replace with your model prediction logic)
dates = pd.date_range(start="2025-10-01", periods=14)
forecast = pd.DataFrame({
    "Date": dates,
    "Predicted Sales": np.random.randint(200, 1000, 14)
})

st.line_chart(forecast.set_index("Date"))

# Display insights
avg_sales = forecast["Predicted Sales"].mean()
max_sales = forecast["Predicted Sales"].max()
st.markdown(
    f"""
    <div class='card'>
      <strong>Forecast Summary:</strong>
      <p>Average daily predicted sales: <b>{avg_sales:.0f}</b> units</p>
      <p>Expected peak day sales: <b>{max_sales}</b> units</p>
      <p style='color:#475569;'>Your AI model predicts stable demand for the next two weeks.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
