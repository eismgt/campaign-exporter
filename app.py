import streamlit as st
import os
from smartlead_client import SmartleadClient
from lead_processor import process_campaign_leads
from csv_exporter import leads_to_csv, generate_filename

# Hardcoded credentials
USERNAME = "admin"
PASSWORD = "team@hyperke"

st.set_page_config(
    page_title="Smartlead Campaign Exporter",
    page_icon="📧",
    layout="wide"
)

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Logout functionality
if st.session_state.authenticated:
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

# Login Page
if not st.session_state.authenticated:
    st.markdown("""
        <style>
        /* Remove Streamlit's default padding */
        .main .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            padding-left: 20px !important;
            padding-right: 20px !important;
            max-width: 100% !important;
        }

        /* Full viewport height centering */
        .login-full-page {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            width: 100%;
        }

        /* Login container styling */
        .login-container {
            width: 100%;
            max-width: 380px;
            padding: 36px 36px 32px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            text-align: center;
        }

        .login-title {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 6px;
            color: #1f2937;
        }

        .login-subtitle {
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 24px;
        }

        /* Hide Streamlit's default elements on login page */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Responsive adjustments */
        @media (max-width: 640px) {
            .login-container {
                max-width: 100%;
                padding: 28px 24px 24px;
                border-radius: 8px;
            }
            .main .block-container {
                padding-left: 10px !important;
                padding-right: 10px !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="login-full-page">
            <div class="login-container">
                <div class="login-title">📧 Campaign Exporter</div>
                <div class="login-subtitle">Please log in to continue</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    username = st.text_input(
        "Username",
        placeholder="Enter your username",
        key="login_username"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password"
    )

    if st.button("🔐 Login", type="primary", use_container_width=True):
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    st.stop()

# Main App (shown only when authenticated)
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
try:
    client = SmartleadClient(api_key)
    st.success("✅ Connected to Smartlead API")
except Exception as e:
    st.error(f"Failed to initialize API client: {e}")
    st.stop()

# Campaign Selection
st.header("1. Select Campaigns")

try:
    campaigns = client.get_campaigns()

    if not campaigns:
        st.warning("No campaigns found.")
        st.stop()

    # Create a mapping of campaign ID to campaign object
    campaign_by_id = {c["id"]: c for c in campaigns}

    # Create display names with status
    campaign_options = {}
    for c in campaigns:
        name = c.get("name", f"Campaign {c['id']}")
        status = c.get("status", "UNKNOWN")
        display_name = f"{name} (#{c['id']}) - {status}"
        campaign_options[display_name] = c

    # Tab interface for both selection methods
    tab1, tab2 = st.tabs(["🔍 Search & Select", "🆔 Enter Campaign IDs"])

    with tab1:
        selected_campaign_names = st.multiselect(
            "Search and select campaigns to export",
            options=list(campaign_options.keys()),
            default=[],
            placeholder="Type to search campaigns...",
            label_visibility="visible",
            key="multiselect_tab"
        )
        selected_campaigns = [campaign_options[name] for name in selected_campaign_names]

    with tab2:
        id_input = st.text_input(
            "Enter Campaign IDs (comma-separated)",
            placeholder="e.g., 12345, 67890, 54321",
            help="Enter multiple campaign IDs separated by commas",
            key="id_input_tab"
        )

        selected_by_id = []
        invalid_ids = []
        not_found_ids = []

        if id_input.strip():
            # Parse and validate Campaign IDs
            input_ids = [id_str.strip() for id_str in id_input.split(",") if id_str.strip()]

            for id_str in input_ids:
                # Try to convert to integer
                try:
                    campaign_id = int(id_str)
                except ValueError:
                    invalid_ids.append(id_str)
                    continue

                # Check if campaign exists
                if campaign_id in campaign_by_id:
                    selected_by_id.append(campaign_by_id[campaign_id])
                else:
                    not_found_ids.append(str(campaign_id))

            # Display validation messages
            if invalid_ids:
                st.error(f"❌ Invalid Campaign ID format: {', '.join(invalid_ids)}")

            if not_found_ids:
                st.warning(f"⚠️ Campaign IDs not found: {', '.join(not_found_ids)}")

            if selected_by_id:
                st.success(f"✅ {len(selected_by_id)} campaign(s) matched by ID")

                # Display matched campaigns for verification
                st.subheader("📋 Matched Campaigns")
                for campaign in selected_by_id:
                    name = campaign.get("name", f"Campaign #{campaign['id']}")
                    status = campaign.get("status", "UNKNOWN")
                    st.markdown(f"- **{name}** (ID: `{campaign['id']}`) — *{status}*")

            # Combine with multiselect selections if any
            selected_campaigns = selected_by_id

    # Combine selections from both tabs
    if selected_campaigns:
        # Get unique campaigns by ID to avoid duplicates
        unique_campaigns = {c["id"]: c for c in selected_campaigns}.values()
        selected_campaigns = list(unique_campaigns)

        if len(selected_campaigns) > 0:
            st.info(f"✅ {len(selected_campaigns)} campaign(s) selected")

except Exception as e:
    st.error(f"Failed to fetch campaigns: {e}")
    st.stop()

# Export Section
st.header("2. Export Leads")

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

            if stats.get("has_engagement_data", False):
                st.caption(f"Bounced excluded: {stats['bounced_excluded']} | Replied excluded: {stats['replied_excluded']} | Duplicates removed: {stats['duplicates_removed']}")
            else:
                st.caption(f"⚠️ API doesn't provide engagement metrics - exported all leads (deduped). Duplicates removed: {stats['duplicates_removed']}")

            # Display leads in a table
            st.subheader(f"📊 Preview ({stats['final']} leads)")

            # Prepare data for display - select key columns
            display_columns = ["email", "first_name", "last_name", "company_name", "website", "location"]
            display_leads = []
            for lead in final_leads:
                row = {col: lead.get(col, "") for col in display_columns}
                display_leads.append(row)

            st.dataframe(
                display_leads,
                use_container_width=True,
                hide_index=True,
                height=400
            )

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
