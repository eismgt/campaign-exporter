import pytest
from lead_processor import filter_not_replied_leads, deduplicate_leads, process_campaign_leads

def test_filter_not_replied_excludes_bounced():
    leads = [
        {"email": "a@example.com", "reply_count": 0, "email_status": "not_replied"},
        {"email": "b@example.com", "reply_count": 0, "email_status": "is_bounced"},
        {"email": "c@example.com", "reply_count": 1, "email_status": "is_replied"},
        {"email": "d@example.com", "reply_count": 0, "email_status": "opened"},
    ]

    result = filter_not_replied_leads(leads)

    assert len(result) == 2
    assert result[0]["email"] == "a@example.com"
    assert result[1]["email"] == "d@example.com"

def test_deduplicate_keeps_most_recent():
    leads = [
        {"email": "test@example.com", "updated_at": "2024-01-01T00:00:00Z", "name": "Old"},
        {"email": "TEST@Example.com", "updated_at": "2024-01-15T00:00:00Z", "name": "New"},
        {"email": "other@example.com", "updated_at": "2024-01-10T00:00:00Z", "name": "Other"},
    ]

    result = deduplicate_leads(leads)

    assert len(result) == 2
    assert result[0]["email"] == "TEST@Example.com"
    assert result[0]["name"] == "New"
    assert result[1]["email"] == "other@example.com"

def test_deduplicate_handles_missing_updated_at():
    leads = [
        {"email": "a@example.com"},
        {"email": "A@EXAMPLE.COM", "updated_at": "2024-01-15T00:00:00Z"},
    ]

    result = deduplicate_leads(leads)

    assert len(result) == 1
    # The one with updated_at should come first and be kept
    assert result[0]["email"] == "A@EXAMPLE.COM"

def test_process_campaign_leads_stats():
    leads = [
        {"email": "a@example.com", "reply_count": 0, "email_status": "not_replied", "updated_at": "2024-01-01T00:00:00Z"},
        {"email": "a@example.com", "reply_count": 0, "email_status": "not_replied", "updated_at": "2024-01-15T00:00:00Z"},  # dup
        {"email": "b@example.com", "reply_count": 1, "email_status": "replied", "updated_at": "2024-01-01T00:00:00Z"},
        {"email": "c@example.com", "reply_count": 0, "email_status": "is_bounced", "updated_at": "2024-01-01T00:00:00Z"},
    ]
    result = process_campaign_leads(leads)
    assert result["stats"]["original"] == 4
    assert result["stats"]["bounced_excluded"] == 1
    assert result["stats"]["replied_excluded"] == 1
    assert result["stats"]["duplicates_removed"] == 1
    assert result["stats"]["final"] == 1
