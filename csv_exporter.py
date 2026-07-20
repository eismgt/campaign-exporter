import csv
import io
from typing import List, Dict

def leads_to_csv(leads: List[Dict]) -> str:
    """Convert leads to CSV string."""
    if not leads:
        # Return minimal CSV with just email header if no leads
        return "email\n"

    # Collect all unique field names from all leads
    fieldnames = set()
    for lead in leads:
        fieldnames.update(lead.keys())

    # Sort for consistent column order (email first, then others alphabetically)
    fieldnames = sorted(fieldnames, key=lambda x: (x != "email", x))

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(leads)

    return output.getvalue()


def generate_filename(campaign_names: List[str]) -> str:
    """Generate filename for export."""
    if len(campaign_names) == 1:
        return f"{campaign_names[0]}_not_replied_leads.csv"
    return "combined_not_replied_leads.csv"
