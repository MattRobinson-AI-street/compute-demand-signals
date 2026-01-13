"""Filing ingestion logic for SEC data."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from aistreet.config import RAW_DATA_DIR, SUPPORTED_FORMS
from aistreet.db.repository import Source, get_source_by_text_path, insert_source
from aistreet.sec.client import SECClient
from aistreet.sec.parser import html_to_text


def parse_lookback_period(since: str) -> str:
    """
    Parse a lookback period string and return ISO date.

    Args:
        since: String like "7d", "30d", "90d"

    Returns:
        ISO date string (yyyy-mm-dd)
    """
    if since.endswith("d"):
        days = int(since[:-1])
        cutoff = datetime.now() - timedelta(days=days)
        return cutoff.strftime("%Y-%m-%d")
    else:
        # Assume it's already an ISO date
        return since


def get_company_name(submissions: dict) -> str:
    """Extract company name from submissions JSON."""
    return submissions.get("name", "Unknown")


def ingest_filings(
    ciks: list[str],
    form_types: set[str],
    since_date: str,
    client: Optional[SECClient] = None,
) -> tuple[int, int]:
    """
    Ingest filings for given CIKs.

    Args:
        ciks: List of CIK strings
        form_types: Set of form types to ingest (e.g., {"8-K", "10-Q", "10-K"})
        since_date: ISO date string for lookback period
        client: Optional SEC client (creates new one if not provided)

    Returns:
        Tuple of (total_filings_found, new_filings_ingested)
    """
    if client is None:
        client = SECClient()

    # Validate form types
    invalid_forms = form_types - SUPPORTED_FORMS
    if invalid_forms:
        raise ValueError(f"Unsupported form types: {invalid_forms}")

    total_found = 0
    total_ingested = 0

    for cik in ciks:
        cik = cik.strip()
        if not cik:
            continue

        print(f"Fetching submissions for CIK {cik}...")
        submissions = client.get_submissions(cik)

        if not submissions:
            print(f"  No submissions found for CIK {cik}")
            continue

        company_name = get_company_name(submissions)
        recent_filings = submissions.get("filings", {}).get("recent", {})

        if not recent_filings:
            print(f"  No recent filings for {company_name}")
            continue

        # Extract filing arrays
        forms = recent_filings.get("form", [])
        filing_dates = recent_filings.get("filingDate", [])
        accession_numbers = recent_filings.get("accessionNumber", [])
        primary_documents = recent_filings.get("primaryDocument", [])

        # Process each filing
        for i, form in enumerate(forms):
            if form not in form_types:
                continue

            filing_date = filing_dates[i]
            if filing_date < since_date:
                continue

            accession = accession_numbers[i]
            primary_doc = primary_documents[i]

            total_found += 1

            # Build local storage path
            # Format: data/raw/sec/{cik}/{accession}/{primary_document}
            local_dir = RAW_DATA_DIR / cik / accession.replace("-", "")
            local_path = local_dir / primary_doc

            # Check if already ingested
            text_path_str = str(local_path.relative_to(RAW_DATA_DIR.parent.parent))
            existing_source = get_source_by_text_path(text_path_str)

            if existing_source:
                continue

            # Download filing
            print(f"  Downloading {form} from {filing_date} (accession: {accession})...")
            content = client.download_filing(cik, accession, primary_doc)

            if not content:
                print(f"    Failed to download {accession}/{primary_doc}")
                continue

            # Save to disk
            local_dir.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(content)

            # Convert to text and save
            text_content = html_to_text(content)
            text_path = local_path.with_suffix(".txt")
            text_path.write_text(text_content, encoding="utf-8")

            # Insert into database
            url = client.get_filing_url(cik, accession, primary_doc)
            title = f"{form} - {accession}"

            source = Source(
                company=company_name,
                cik=cik,
                form_type=form,
                filing_date=filing_date,
                title=title,
                url=url,
                text_path=str(text_path.relative_to(RAW_DATA_DIR.parent.parent)),
            )

            source_id = insert_source(source)
            if source_id:
                total_ingested += 1
                print(f"    Ingested: {company_name} {form} (source_id={source_id})")

    return total_found, total_ingested
