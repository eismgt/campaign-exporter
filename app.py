import streamlit as st
import os

st.set_page_config(
    page_title="Smartlead Campaign Exporter",
    page_icon="📧",
    layout="wide"
)

st.title("📧 Smartlead Campaign Exporter")
st.markdown("Export leads who haven't replied from selected campaigns.")

# Check for API key
api_key = st.secrets.get("SMARTLEAD_API_KEY")

if not api_key or api_key == "your_api_key_here":
    st.error("""
    **API Key not configured!**

    Please set your Smartlead API key in `.streamlit/secrets.toml`:
    ```toml
    SMARTLEAD_API_KEY = "your_actual_api_key"
    ```

    Get your API key from: https://smartlead.ai/app/settings/api-settings
    """)
    st.stop()

st.success("✅ API key configured")
st.caption(f"Using API key: {api_key[:8]}...")
