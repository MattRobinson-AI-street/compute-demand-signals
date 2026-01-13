"""SEC EDGAR API client with rate limiting."""

import time
from typing import Any, Optional

import requests

from aistreet.config import (
    SEC_ARCHIVES_BASE_URL,
    SEC_RATE_LIMIT_DELAY,
    SEC_SUBMISSIONS_URL,
    SEC_USER_AGENT,
)


class SECClient:
    """Client for interacting with SEC EDGAR APIs."""

    def __init__(self, user_agent: str = SEC_USER_AGENT):
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self._last_request_time = 0.0

    def _rate_limit(self) -> None:
        """Enforce rate limiting (max 10 requests per second)."""
        elapsed = time.time() - self._last_request_time
        if elapsed < SEC_RATE_LIMIT_DELAY:
            time.sleep(SEC_RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()

    def get_submissions(self, cik: str) -> Optional[dict[str, Any]]:
        """
        Fetch company submissions data from SEC.

        Args:
            cik: Company CIK (Central Index Key), zero-padded to 10 digits

        Returns:
            Submissions JSON data or None if not found
        """
        self._rate_limit()

        # Ensure CIK is zero-padded to 10 digits
        cik_padded = cik.zfill(10)
        url = SEC_SUBMISSIONS_URL.format(cik=int(cik_padded))

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
        except requests.exceptions.RequestException as e:
            print(f"Error fetching submissions for CIK {cik}: {e}")
            return None

    def download_filing(self, cik: str, accession: str, primary_document: str) -> Optional[bytes]:
        """
        Download a filing document from SEC Archives.

        Args:
            cik: Company CIK
            accession: Accession number (with dashes removed for URL)
            primary_document: Primary document filename

        Returns:
            Document content as bytes or None if not found
        """
        self._rate_limit()

        # Remove dashes from accession number for URL
        accession_no_dashes = accession.replace("-", "")

        # Build URL: https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{document}
        url = f"{SEC_ARCHIVES_BASE_URL}/{cik}/{accession_no_dashes}/{primary_document}"

        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            return response.content
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
        except requests.exceptions.RequestException as e:
            print(f"Error downloading filing {accession}/{primary_document}: {e}")
            return None

    def get_filing_url(self, cik: str, accession: str, primary_document: str) -> str:
        """
        Construct the SEC Archives URL for a filing.

        Args:
            cik: Company CIK
            accession: Accession number (with dashes)
            primary_document: Primary document filename

        Returns:
            Full URL to the filing on SEC website
        """
        accession_no_dashes = accession.replace("-", "")
        return f"{SEC_ARCHIVES_BASE_URL}/{cik}/{accession_no_dashes}/{primary_document}"
