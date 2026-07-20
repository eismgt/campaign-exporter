# Smartlead Campaign Exporter

Export leads who haven't replied from selected Smartlead campaigns.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure API key in `.streamlit/secrets.toml`:
   ```toml
   SMARTLEAD_API_KEY = "your_api_key_here"
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Select a client (if you have multiple)
2. Search and select campaigns
3. Click "Export Leads" to download CSV
