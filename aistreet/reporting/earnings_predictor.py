"""Predict upcoming earnings dates based on historical patterns."""

from datetime import datetime, timedelta
from typing import Optional

from aistreet.db.repository import get_all_sources


# Known quarterly patterns for major tech companies (fiscal year end dates)
# These companies typically file 10-Q 30-45 days after quarter end
FISCAL_CALENDARS = {
    "MICROSOFT CORP": {"fiscal_year_end": "6/30", "q_offset_days": [3, 6, 9, 12]},
    "ALPHABET INC": {"fiscal_year_end": "12/31", "q_offset_days": [3, 6, 9, 12]},
    "AMAZON COM INC": {"fiscal_year_end": "12/31", "q_offset_days": [3, 6, 9, 12]},
    "META PLATFORMS INC": {"fiscal_year_end": "12/31", "q_offset_days": [3, 6, 9, 12]},
    "NVIDIA CORP": {"fiscal_year_end": "1/31", "q_offset_days": [3, 6, 9, 12]},
    "ADVANCED MICRO DEVICES INC": {
        "fiscal_year_end": "12/31",
        "q_offset_days": [3, 6, 9, 12],
    },
    "BROADCOM INC": {"fiscal_year_end": "10/31", "q_offset_days": [3, 6, 9, 12]},
    "ARISTA NETWORKS INC": {
        "fiscal_year_end": "12/31",
        "q_offset_days": [3, 6, 9, 12],
    },
    "EQUINIX INC": {"fiscal_year_end": "12/31", "q_offset_days": [3, 6, 9, 12]},
    "DIGITAL REALTY TRUST INC": {
        "fiscal_year_end": "12/31",
        "q_offset_days": [3, 6, 9, 12],
    },
    "VERTIV HOLDINGS CO": {"fiscal_year_end": "12/31", "q_offset_days": [3, 6, 9, 12]},
    "ACUITY INC. (DE)": {"fiscal_year_end": "9/30", "q_offset_days": [3, 6, 9, 12]},
    "Alphabet Inc.": {"fiscal_year_end": "12/31", "q_offset_days": [3, 6, 9, 12]},
    "Meta Platforms, Inc.": {"fiscal_year_end": "12/31", "q_offset_days": [3, 6, 9, 12]},
    "Broadcom Inc.": {"fiscal_year_end": "10/31", "q_offset_days": [3, 6, 9, 12]},
}

# Typical filing windows after quarter end
FILING_DELAY_DAYS = 35  # Most companies file 30-45 days after quarter end


def get_next_quarter_end(fiscal_year_end: str, reference_date: Optional[datetime] = None) -> datetime:
    """
    Get the next fiscal quarter end date.

    Args:
        fiscal_year_end: Fiscal year end in "M/D" format (e.g., "6/30")
        reference_date: Reference date (defaults to today)

    Returns:
        Next quarter end date
    """
    if reference_date is None:
        reference_date = datetime.now()

    # Parse fiscal year end
    month, day = map(int, fiscal_year_end.split("/"))

    # Calculate quarter ends for the current fiscal year
    year = reference_date.year
    quarter_ends = []

    # Adjust year for fiscal calendars that don't match calendar year
    if month < reference_date.month:
        year += 1

    for q_offset in [0, 3, 6, 9]:
        quarter_month = (month + q_offset - 1) % 12 + 1
        quarter_year = year if (month + q_offset) <= 12 else year + 1

        try:
            quarter_end = datetime(quarter_year, quarter_month, day)
            if quarter_end > reference_date:
                quarter_ends.append(quarter_end)
        except ValueError:
            # Handle invalid dates (e.g., Feb 30)
            # Use last day of month instead
            if quarter_month == 2:
                # February - use 28 or 29
                is_leap = (
                    quarter_year % 4 == 0
                    and (quarter_year % 100 != 0 or quarter_year % 400 == 0)
                )
                quarter_end = datetime(quarter_year, 2, 29 if is_leap else 28)
            else:
                # Use last day of month
                next_month = quarter_month % 12 + 1
                next_year = quarter_year if next_month > 1 else quarter_year + 1
                quarter_end = datetime(next_year, next_month, 1) - timedelta(days=1)

            if quarter_end > reference_date:
                quarter_ends.append(quarter_end)

    return min(quarter_ends) if quarter_ends else None


def predict_upcoming_filings(days_ahead: int = 60) -> list[dict]:
    """
    Predict upcoming 10-Q and 10-K filings.

    Args:
        days_ahead: Number of days to look ahead (default: 60)

    Returns:
        List of predicted filings with company, expected_date, form_type
    """
    today = datetime.now()
    cutoff = today + timedelta(days=days_ahead)
    predictions = []

    # Get historical data to improve predictions
    historical_sources = get_all_sources()
    historical_by_company = {}
    for source in historical_sources:
        if source.company not in historical_by_company:
            historical_by_company[source.company] = []
        historical_by_company[source.company].append(
            {"form_type": source.form_type, "filing_date": source.filing_date}
        )

    for company, calendar_info in FISCAL_CALENDARS.items():
        fiscal_year_end = calendar_info["fiscal_year_end"]

        # Get next quarter end
        next_quarter_end = get_next_quarter_end(fiscal_year_end, today)

        if next_quarter_end is None:
            continue

        # Estimate filing date (typically 30-45 days after quarter end)
        estimated_filing_date = next_quarter_end + timedelta(days=FILING_DELAY_DAYS)

        # Check if historical data exists for this company
        if company in historical_by_company:
            # Use historical average delay if available
            recent_filings = historical_by_company[company]
            if recent_filings:
                # Calculate average delay (simplified - would need quarter end dates)
                # For now, use the default
                pass

        # Only include if within our prediction window
        if today <= estimated_filing_date <= cutoff:
            # Determine form type based on quarter
            form_type = "10-Q"  # Most filings are quarterly
            quarter_month = next_quarter_end.month
            fy_month = int(fiscal_year_end.split("/")[0])

            # Check if this is fiscal year end (10-K instead of 10-Q)
            if quarter_month == fy_month:
                form_type = "10-K"

            predictions.append(
                {
                    "company": company,
                    "expected_date": estimated_filing_date.strftime("%Y-%m-%d"),
                    "form_type": form_type,
                    "quarter_end": next_quarter_end.strftime("%Y-%m-%d"),
                    "confidence": "estimated",  # Could be 'high', 'medium', 'low' based on historical accuracy
                }
            )

    # Sort by expected date
    predictions.sort(key=lambda x: x["expected_date"])

    return predictions


def get_filing_window(company: str, days_ahead: int = 90) -> Optional[dict]:
    """
    Get the next expected filing window for a specific company.

    Args:
        company: Company name
        days_ahead: Days to look ahead

    Returns:
        Dict with next filing info or None
    """
    predictions = predict_upcoming_filings(days_ahead)
    for pred in predictions:
        if pred["company"] == company:
            return pred
    return None
