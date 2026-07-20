import pytest
import io
import csv
from csv_exporter import leads_to_csv

def test_leads_to_csv_basic():
    leads = [
        {"email": "test@example.com", "first_name": "John", "reply_count": 0},
        {"email": "another@example.com", "first_name": "Jane", "reply_count": 0},
    ]

    csv_data = leads_to_csv(leads)

    # Parse CSV to verify
    reader = csv.DictReader(io.StringIO(csv_data))
    rows = list(reader)

    assert len(rows) == 2
    assert rows[0]["email"] == "test@example.com"
    assert rows[1]["first_name"] == "Jane"

def test_leads_to_csv_includes_all_fields():
    leads = [
        {"email": "test@example.com", "custom_field": "value", "another": 123},
    ]

    csv_data = leads_to_csv(leads)
    reader = csv.DictReader(io.StringIO(csv_data))
    rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["custom_field"] == "value"
    assert rows[0]["another"] == "123"

def test_leads_to_csv_empty_list():
    csv_data = leads_to_csv([])
    assert csv_data == "email\n"

def test_leads_to_csv_inconsistent_fields():
    """Test that leads with missing fields are handled correctly."""
    leads = [
        {"email": "a@example.com", "name": "John"},
        {"email": "b@example.com"},  # missing 'name'
        {"email": "c@example.com", "name": "Jane", "phone": "555-1234"},  # extra field
    ]

    csv_data = leads_to_csv(leads)
    reader = csv.DictReader(io.StringIO(csv_data))
    rows = list(reader)

    assert len(rows) == 3
    # All rows should have email
    assert rows[0]["email"] == "a@example.com"
    assert rows[1]["email"] == "b@example.com"
    # Row 1 (b@example.com) should have empty string for missing 'name'
    assert rows[1].get("name", "") == ""

def test_leads_to_csv_special_characters():
    """Test that special characters are properly escaped."""
    leads = [
        {"email": 'test,comma@example.com', "name": 'John "The Boss" O\'Brien'},
    ]

    csv_data = leads_to_csv(leads)
    # Parse back to verify proper escaping
    reader = csv.DictReader(io.StringIO(csv_data))
    rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["email"] == 'test,comma@example.com'
    assert rows[0]["name"] == 'John "The Boss" O\'Brien'
