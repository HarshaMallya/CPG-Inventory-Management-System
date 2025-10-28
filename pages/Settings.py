import streamlit as st


if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Please log in to access this page.")
    st.stop()


st.set_page_config(page_title="Settings", layout="wide")

st.markdown("<div class='card'><h3>⚙️ Settings</h3></div>", unsafe_allow_html=True)

st.markdown("You can configure basic parameters below:")

# Settings form
with st.form("settings_form"):
    reorder_threshold = st.slider("Default Reorder Threshold", 10, 100, 30)
    theme = st.selectbox("Theme Mode", ["Pastel Light", "Corporate Light (Default)", "Dark"])
    notifications = st.checkbox("Enable Stock Alerts", True)
    submitted = st.form_submit_button("Save Settings")
    if submitted:
        st.success("Settings saved successfully!")

st.markdown(
    """
    <div class='card'>
      <p style='color:#475569;'>💡 Tip: To apply advanced custom themes, edit <b>assets/custom.css</b>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
