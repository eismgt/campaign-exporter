from typing import List, Dict

def filter_not_replied_leads(leads: List[Dict]) -> List[Dict]:
    """Filter leads where reply_count == 0 and not bounced.

    NOTE: If reply_count/email_status fields are not available (API limitation),
    this returns all leads. Filtering is best-effort based on available data.
    """
    filtered = []
    has_engagement_data = any("reply_count" in l or "email_status" in l for l in leads)

    if not has_engagement_data:
        # API doesn't provide engagement data - return all leads
        return leads

    for lead in leads:
        reply_count = int(lead.get("reply_count", 0) or 0)
        email_status = lead.get("email_status", "").lower()

        # reply_count must be 0 (or missing/empty which we treat as 0)
        if reply_count != 0:
            continue

        # Exclude bounced leads
        if email_status == "is_bounced" or email_status == "bounced":
            continue

        filtered.append(lead)

    return filtered


def deduplicate_leads(leads: List[Dict]) -> List[Dict]:
    """Deduplicate leads by email, keeping most recent (by updated_at)."""
    # Sort by updated_at descending (most recent first)
    # If updated_at is missing, treat as empty string (will sort to end)
    sorted_leads = sorted(
        leads,
        key=lambda x: x.get("updated_at", ""),
        reverse=True
    )

    seen_emails = set()
    unique_leads = []

    for lead in sorted_leads:
        email = lead.get("email", "").lower().strip()
        if not email:
            continue

        if email not in seen_emails:
            seen_emails.add(email)
            unique_leads.append(lead)

    return unique_leads


def process_campaign_leads(all_leads: List[Dict]) -> Dict:
    """Process all leads from multiple campaigns: filter, dedupe, return stats."""

    # Step 1: Filter not replied (excluding bounced)
    not_replied = filter_not_replied_leads(all_leads)

    # Step 2: Deduplicate
    final_leads = deduplicate_leads(not_replied)

    # Calculate stats
    original_count = len(all_leads)
    has_engagement_data = any("reply_count" in l or "email_status" in l for l in all_leads)

    if has_engagement_data:
        bounced_count = sum(1 for l in all_leads if l.get("email_status", "").lower() in ["is_bounced", "bounced"])
        replied_count = sum(1 for l in all_leads if l.get("reply_count", 0) > 0)
    else:
        bounced_count = 0
        replied_count = 0

    final_count = len(final_leads)
    duplicates_removed = len(not_replied) - final_count

    return {
        "leads": final_leads,
        "stats": {
            "original": original_count,
            "bounced_excluded": bounced_count,
            "replied_excluded": replied_count,
            "duplicates_removed": duplicates_removed,
            "final": final_count,
            "has_engagement_data": has_engagement_data,
        }
    }
