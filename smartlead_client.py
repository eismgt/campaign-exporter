import requests

class SmartleadClient:
    """Client for Smartlead API."""

    BASE_URL = "https://server.smartlead.ai/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    @property
    def base_url(self):
        return self.BASE_URL

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        """Make GET request to Smartlead API."""
        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        params["api_key"] = self.api_key

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_all_clients(self) -> list:
        """Get all clients."""
        return self._get("/clients")

    def get_campaigns(self, client_id: int = None) -> list:
        """Get campaigns, optionally filtered by client."""
        params = {}
        if client_id:
            params["client_id"] = client_id
        return self._get("/campaigns", params)

    def get_campaign_leads(self, campaign_id: int) -> list:
        """Get all leads for a campaign (handles pagination)."""
        all_leads = []
        offset = 0
        limit = 100  # API max limit per request

        while True:
            params = {"offset": offset, "limit": limit}
            result = self._get(f"/campaigns/{campaign_id}/leads", params)

            # Handle different response formats
            if isinstance(result, dict):
                # API returns {"total_leads": "N", "data": [...]}
                leads_data = result.get("data", [])
                total_leads = int(result.get("total_leads", 0))

                # Flatten nested lead structure
                for item in leads_data:
                    if isinstance(item, dict) and "lead" in item:
                        # Merge campaign-level fields with lead data
                        lead = item["lead"].copy()
                        # Add campaign-specific fields
                        lead["campaign_lead_map_id"] = item.get("campaign_lead_map_id")
                        lead["lead_status"] = item.get("status")
                        lead["created_at"] = item.get("created_at")
                        all_leads.append(lead)
                    else:
                        all_leads.append(item)

                # Check if we've fetched all leads
                if len(all_leads) >= total_leads or not leads_data:
                    break

                offset += limit
            else:
                # Fallback for unexpected format
                return result if isinstance(result, list) else []

        return all_leads

    def delete_campaign_lead(self, campaign_id: int, lead_id: int) -> bool:
        """Delete a lead from a campaign. Reserved for V2."""
        url = f"{self.BASE_URL}/campaigns/{campaign_id}/leads/{lead_id}"
        params = {"api_key": self.api_key}
        response = requests.delete(url, params=params, timeout=30)
        response.raise_for_status()
        return response.status_code == 200
