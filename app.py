import streamlit as st
import os
from smartlead_client import SmartleadClient

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

# Initialize client
client = SmartleadClient(api_key)

# Client Selection
st.header("1. Select Client")

try:
    all_clients = client.get_all_clients()

    if not all_clients:
        st.error("No clients found. Please create a client in Smartlead first.")
        st.stop()
    elif len(all_clients) == 1:
        st.info("Only one client available - automatically selected")
        selected_client_id = all_clients[0]["id"]
    else:
        client_options = {c.get("name", f"Client {c['id']}"): c["id"] for c in all_clients}
        selected_client_name = st.selectbox(
            "Choose a client",
            options=list(client_options.keys()),
            index=0
        )
        selected_client_id = client_options[selected_client_name]

except Exception as e:
    st.error(f"Failed to fetch clients: {e}")
    st.stop()

# Campaign Selection
st.header("2. Select Campaigns")

if selected_client_id:
    try:
        campaigns = client.get_campaigns(client_id=selected_client_id)

        if not campaigns:
            st.warning("No campaigns found for this client.")
            st.stop()

        # Create display names with status
        campaign_options = {}
        for c in campaigns:
            name = c.get("name", f"Campaign {c['id']}")
            status = c.get("status", "UNKNOWN")
            display_name = f"{name} (#{c['id']}) - {status}"
            campaign_options[display_name] = c

        selected_campaign_names = st.multiselect(
            "Search and select campaigns to export",
            options=list(campaign_options.keys()),
            default=[],
            placeholder="Type to search campaigns...",
            label_visibility="visible"
        )

        selected_campaigns = [campaign_options[name] for name in selected_campaign_names]

        if selected_campaigns:
            st.info(f"✅ {len(selected_campaigns)} campaign(s) selected")

    except Exception as e:
        st.error(f"Failed to fetch campaigns: {e}")
        st.stop()
