# Login.py
import streamlit as st
from pathlib import Path

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Login | CPG-Inventory-Management-System",
    page_icon="🔐",
    layout="centered"
)

# ---------- HIDE SIDEBAR UNTIL LOGIN ----------
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# ---------- PATHS ----------
ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
CSS_FILE = ASSETS / "custom.css"
LOGO_FILE = ASSETS / "logo.png"

# ---------- LOAD CSS ----------
def load_css():
    if CSS_FILE.exists():
        with open(CSS_FILE, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ custom.css not found in /assets folder!")

load_css()

# ---------- CREDENTIALS ----------
USER_CREDENTIALS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "manager": {"password": "manager123", "role": "Manager"},
    "employee": {"password": "employee123", "role": "Employee"}
}

# ---------- AUTO-REDIRECT ----------
if st.session_state.get("authenticated", False):
    st.switch_page("pages/Home.py")

# ---------- LOGIN UI ----------
st.markdown("<div style='text-align:center; margin-top:50px;' class='fade-in'>", unsafe_allow_html=True)

# Load logo safely using Streamlit API
if LOGO_FILE.exists():
    st.image(str(LOGO_FILE), width=130)
else:
    st.warning("⚠️ Logo not found in /assets folder!")

st.markdown(
    """
    <h2 style='color:#111827;'>CPG Inventory Management System</h2>
    <p style='color:#64748b;'>Secure login portal for Admin, Manager, and Employee</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ---------- LOGIN FORM ----------
with st.form("login_form", clear_on_submit=True):
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    submit_btn = st.form_submit_button("Login")

if submit_btn:
    user = USER_CREDENTIALS.get(username)
    if user and password == user["password"]:
        st.session_state["authenticated"] = True
        st.session_state["role"] = user["role"]
        st.session_state["username"] = username
        st.success(f"✅ Welcome {user['role']} {username.capitalize()}!")
        st.switch_page("pages/Home.py")  # ✅ Redirect directly to home
    else:
        st.error("❌ Invalid username or password.")

# ---------- FOOTER ----------
st.markdown(
    """
    <div style='margin-top:40px; text-align:center; color:#94a3b8; font-size:12px'>
        © 2025 CPG-Inventory-Management-System
    </div>
    """,
    unsafe_allow_html=True
)
