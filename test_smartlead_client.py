import pytest
from unittest.mock import Mock, patch
from smartlead_client import SmartleadClient

@pytest.fixture
def client():
    return SmartleadClient("test_api_key")

def test_init(client):
    assert client.api_key == "test_api_key"
    assert client.base_url == "https://server.smartlead.ai/api/v1"

@patch('requests.get')
def test_get_all_clients(mock_get, client):
    mock_get.return_value.json.return_value = [
        {"id": 1, "name": "Client A"},
        {"id": 2, "name": "Client B"}
    ]

    clients = client.get_all_clients()

    assert len(clients) == 2
    assert clients[0]["id"] == 1
    mock_get.assert_called_once()

@patch('requests.get')
def test_get_campaigns(mock_get, client):
    mock_get.return_value.json.return_value = [
        {"id": 123, "name": "Campaign 1", "status": "ACTIVE"},
        {"id": 456, "name": "Campaign 2", "status": "COMPLETED"}
    ]

    campaigns = client.get_campaigns(client_id=1)

    assert len(campaigns) == 2
    assert campaigns[0]["status"] == "ACTIVE"

@patch('requests.get')
def test_get_campaign_leads(mock_get, client):
    mock_get.return_value.json.return_value = {
        "leads": [
            {"id": 1, "email": "test@example.com", "reply_count": 0, "email_status": "not_replied", "updated_at": "2024-01-15T10:00:00Z"},
            {"id": 2, "email": "bounced@example.com", "reply_count": 0, "email_status": "is_bounced", "updated_at": "2024-01-15T10:00:00Z"}
        ]
    }

    leads = client.get_campaign_leads(campaign_id=123)

    assert len(leads) == 2
    assert leads[0]["email"] == "test@example.com"
