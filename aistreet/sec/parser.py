"""HTML to text conversion for SEC filings."""

from bs4 import BeautifulSoup


def html_to_text(html_content: bytes) -> str:
    """
    Convert HTML filing content to plain text.

    Args:
        html_content: Raw HTML bytes from filing

    Returns:
        Plain text with minimal formatting
    """
    try:
        # Try to decode as UTF-8, fall back to latin-1
        try:
            text_content = html_content.decode("utf-8")
        except UnicodeDecodeError:
            text_content = html_content.decode("latin-1")

        # Parse HTML
        soup = BeautifulSoup(text_content, "lxml")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text(separator=" ", strip=True)

        # Collapse multiple spaces and newlines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        return text

    except Exception as e:
        print(f"Error parsing HTML: {e}")
        # Fall back to basic text extraction
        try:
            return html_content.decode("utf-8", errors="ignore")
        except Exception:
            return html_content.decode("latin-1", errors="ignore")
