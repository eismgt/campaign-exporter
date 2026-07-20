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
        """Get all leads for a campaign."""
        result = self._get(f"/campaigns/{campaign_id}/leads")
        # Handle different response formats
        if isinstance(result, dict):
            return result.get("leads", [])
        return result if isinstance(result, list) else []

    def delete_campaign_lead(self, campaign_id: int, lead_id: int) -> bool:
        """Delete a lead from a campaign. Reserved for V2."""
        url = f"{self.BASE_URL}/campaigns/{campaign_id}/leads/{lead_id}"
        params = {"api_key": self.api_key}
        response = requests.delete(url, params=params, timeout=30)
        response.raise_for_status()
        return response.status_code == 200
