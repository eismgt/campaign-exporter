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
