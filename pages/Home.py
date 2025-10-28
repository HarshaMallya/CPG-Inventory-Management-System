# pages/Home.py
import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="CPG-Inventory-Management-System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- AUTH GUARD ----------
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Please log in first!")
    st.stop()

# ---------- SHOW SIDEBAR ----------
show_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {visibility: visible;}
        header {visibility: visible;}
    </style>
"""
st.markdown(show_sidebar_style, unsafe_allow_html=True)

# ---------- PATHS ----------
ROOT = Path(__file__).parent.parent  # Go up one level to reach project root
ASSETS = ROOT / "assets"
CSS_FILE = ASSETS / "custom.css"
LOGO_FILE = ASSETS / "logo.png"

# ---------- LOAD CSS ----------
def load_css():
    """Load CSS even if Home.py is inside /pages"""
    if CSS_FILE.exists():
        with open(CSS_FILE, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ custom.css not found in /assets folder!")

load_css()

# ---------- SIDEBAR ----------
with st.sidebar:
    # Logo
    if LOGO_FILE.exists():
        st.image(str(LOGO_FILE), width=180)
    else:
        st.warning("⚠️ Logo not found in /assets folder!")

    st.markdown("<div class='sidebar-title'>CPG-Inventory-Management-System</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**Navigation**")
    st.markdown("- Home")
    st.markdown("- Inventory Overview")
    st.markdown("- AI Forecast")
    st.markdown("- Performance Analytics")
    st.markdown("- Settings")
    st.markdown("---")

    # Logout Button
    if st.button("🚪 Logout"):
        for key in ["authenticated", "username", "role"]:
            st.session_state.pop(key, None)
        st.success("✅ Logged out successfully!")
        st.switch_page("Login.py")

    st.markdown("© 2025 Harsha Mallya B")

# ---------- HEADER ----------
st.markdown("<div style='text-align:center; margin-top:40px;' class='fade-in'>", unsafe_allow_html=True)

if LOGO_FILE.exists():
    st.image(str(LOGO_FILE), width=160)
else:
    st.warning("⚠️ Logo not found in /assets folder!")

st.markdown(
    """
    <h1 style="margin-top: 15px; font-size: 42px; color: #111827;">CPG Inventory Management System</h1>
    <p style="color: #64748b; font-size: 18px;">AI-powered forecasting and smart stock tracking for modern CPG companies.</p>
    </div>
    <hr style='margin: 30px 0;'>
    """,
    unsafe_allow_html=True,
)

# ---------- SAMPLE DATA ----------
def sample_data():
    rng = pd.date_range(end=datetime.date.today(), periods=30, freq="D")
    sales = pd.DataFrame({
        "date": rng,
        "product_A": np.random.randint(5, 50, size=len(rng)),
        "product_B": np.random.randint(2, 30, size=len(rng)),
    })
    inventory = pd.DataFrame({
        "product_id": [f"P{i:03d}" for i in range(1, 11)],
        "name": [f"Product {i}" for i in range(1, 11)],
        "stock": np.random.randint(0, 500, size=10),
        "reorder_level": np.random.randint(20, 100, size=10),
    })
    return sales, inventory

sales_df, inventory_df = sample_data()

# ---------- KPI ROW ----------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_products = inventory_df.shape[0]
out_of_stock = int((inventory_df["stock"] == 0).sum())
avg_daily_sales = int(sales_df.drop(columns=["date"]).sum(axis=1).mean())
low_stock_count = int((inventory_df["stock"] <= inventory_df["reorder_level"]).sum())

kpi1.markdown(f"<div class='card kpi'><div class='kpi'>Total Products</div><div class='kpi-value'>{total_products}</div></div>", unsafe_allow_html=True)
kpi2.markdown(f"<div class='card kpi'><div class='kpi'>Out of Stock</div><div class='kpi-value'>{out_of_stock}</div></div>", unsafe_allow_html=True)
kpi3.markdown(f"<div class='card kpi'><div class='kpi'>Avg Daily Sales</div><div class='kpi-value'>{avg_daily_sales}</div></div>", unsafe_allow_html=True)
kpi4.markdown(f"<div class='card kpi'><div class='kpi'>Low Stock Items</div><div class='kpi-value'>{low_stock_count}</div></div>", unsafe_allow_html=True)

# ---------- CHARTS & TABLE ----------
col1, col2 = st.columns((2, 1))
with col1:
    st.markdown("<div class='card'><h3>Sales Trend (Sample)</h3>", unsafe_allow_html=True)
    st.line_chart(sales_df.set_index("date"))
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'><h3>Low Stock Products</h3>", unsafe_allow_html=True)
    st.table(inventory_df.sort_values("stock").head(7).reset_index(drop=True))
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown(
    """
    <div style="margin-top: 40px; text-align:center;">
        <p style="color:#475569;">Hey 👋 — welcome to your CPG Inventory Management Dashboard! 
        Use the sidebar to explore Inventory, Forecast, Analytics, and Settings pages.</p>
        <div style='height:24px'></div>
        <p style='text-align:center; color:#94a3b8; font-size:12px'>
        © 2025 Harsha Mallya B
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

