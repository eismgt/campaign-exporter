import streamlit as st
import os
from smartlead_client import SmartleadClient
from lead_processor import process_campaign_leads
from csv_exporter import leads_to_csv, generate_filename

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

# Initialize session state
if "selected_client_id" not in st.session_state:
    st.session_state.selected_client_id = None

# Initialize client
try:
    client = SmartleadClient(api_key)
    st.success("✅ Connected to Smartlead API")
except Exception as e:
    st.error(f"Failed to initialize API client: {e}")
    st.stop()

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

# Export Section
st.header("3. Export Leads")

if selected_campaigns:
    if st.button("📥 Export Leads (CSV)", type="primary", disabled=not selected_campaigns):

        with st.spinner("Fetching leads..."):
            all_leads = []
            campaign_results = []

            for campaign in selected_campaigns:
                try:
                    leads = client.get_campaign_leads(campaign["id"])
                    all_leads.extend(leads)
                    campaign_results.append({
                        "name": campaign.get("name", f"#{campaign['id']}"),
                        "count": len(leads)
                    })
                    st.caption(f"✓ {campaign.get('name')}: {len(leads)} leads")
                except Exception as e:
                    st.error(f"Failed to fetch leads for {campaign.get('name')}: {e}")

            if not all_leads:
                st.warning("No leads found in selected campaigns.")
                st.stop()

            # Process leads
            result = process_campaign_leads(all_leads)
            final_leads = result["leads"]
            stats = result["stats"]

            # Display stats
            col1, col2, col3 = st.columns(3)
            col1.metric("Original Leads", stats["original"])
            col2.metric("After Filtering", stats["original"] - stats["bounced_excluded"] - stats["replied_excluded"])
            col3.metric("Final Unique", stats["final"])

            st.caption(f"Bounced excluded: {stats['bounced_excluded']} | Replied excluded: {stats['replied_excluded']} | Duplicates removed: {stats['duplicates_removed']}")

            # Generate CSV
            csv_data = leads_to_csv(final_leads)
            campaign_names = [c.get("name", f"campaign_{c['id']}") for c in selected_campaigns]
            filename = generate_filename(campaign_names)

            # Download button
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                type="primary"
            )

else:
    st.info("👆 Select at least one campaign above to export leads.")

# Footer
st.divider()
st.caption("Built for TCPR team | V1 - MVP Release")
