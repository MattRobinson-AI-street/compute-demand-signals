# AI Street - Compute Demand Signal Extraction

A local-first Python pipeline that automatically monitors SEC filings to detect signals about compute infrastructure demand, capacity constraints, and AI investment trends.

## What It Does

This pipeline helps you track the compute infrastructure landscape by:

1. **Monitoring SEC Filings** - Automatically downloads quarterly (10-Q) and annual (10-K) reports, plus material events (8-K) from major tech companies
2. **Extracting Demand Signals** - Uses rule-based pattern matching to identify sentences discussing:
   - Compute demand trends (increasing, decreasing, stable)
   - Infrastructure segments (AI training, inference, general compute)
   - Constraint types (power, chip availability, networking, datacenter capacity)
   - Pricing trends and time horizons
3. **Generating Reports** - Creates weekly markdown reports with statistics, top signals, and company-by-company breakdowns

### Real Example

From Microsoft's Q1 2026 10-Q filing, the system extracted:

> "We continue to identify and evaluate opportunities to expand our datacenter locations and increase our server capacity to meet the evolving needs of our customers, particularly given the growing demand for AI services."

**Classified as:** Demand ↑ | Segment: General | Constraint: Capacity | Confidence: 0.85

## How It Works

### The Pipeline

```
SEC EDGAR → Download Filings → Parse HTML → Extract Signals → Store in SQLite → Generate Reports
```

1. **Ingestion (`sec-ingest`)**: Fetches filings from SEC's official APIs for companies in your universe
2. **Extraction (`extract`)**: Analyzes filing text using keyword patterns to identify compute demand signals
3. **Reporting (`report`)**: Generates markdown reports with signal statistics and analysis

### Signal Attributes

Each extracted signal includes:
- **Quote**: Verbatim sentence from the filing
- **Demand Direction**: up | down | flat | unclear
- **Segment**: training | inference | general
- **Constraint**: power | chips | networking | capacity | other | none
- **Pricing**: up | down | stable | unclear
- **Time Horizon**: now | next_qtr | 6_12mo | 12mo_plus | unclear
- **Confidence**: 0.0 to 1.0 (based on specificity)

### What Makes It Different

- **Deterministic**: No black-box LLMs in v1 - every signal is traceable to specific keywords
- **Auditable**: Full verbatim quotes with sentence references
- **Idempotent**: Safe to re-run without creating duplicates
- **Local-first**: All data stored locally; no cloud dependencies
- **Extensible**: Clean interface to swap in LLM-based extraction later

## Features

- **Web Dashboard**: Interactive HTML website with calendar view and detailed reports
- Fetches filings from SEC EDGAR (8-K, 10-Q, 10-K)
- Deterministic rule-based signal extraction
- Local SQLite storage
- Markdown and HTML report generation
- Fully typed Python codebase
- Clean extractor interface for future LLM integration
- SEC compliant (proper User-Agent, rate limiting)

## 🌐 Live Website

**View the live dashboard at: https://mattrobinson-ai-street.github.io/compute-demand-signals/**

The website includes:
- **[Home](https://mattrobinson-ai-street.github.io/compute-demand-signals/)**: Overview and statistics
- **[Calendar](https://mattrobinson-ai-street.github.io/compute-demand-signals/calendar.html)**: Interactive timeline of filings with clickable SEC links
- **[Report](https://mattrobinson-ai-street.github.io/compute-demand-signals/report.html)**: Detailed signal analysis with top 10 insights

## Installation

### Requirements

- Python 3.10 or higher

### Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install requests beautifulsoup4 click lxml
```

For development (includes pytest):
```bash
pip install requests beautifulsoup4 click lxml pytest
```

## Quick Start

### Run Everything at Once

```bash
python -m aistreet run-all --since 90d
```

This single command:
1. Downloads filings from the past 90 days for all companies in `data/universe.txt`
2. Extracts compute demand signals using pattern matching
3. Generates a report at `reports/weekly_report.md`

**First-time users**: Start with 90 days to get meaningful data. The system is rate-limited and respectful of SEC servers.

### What You'll See

```
Ingesting filings for 11 companies...
Form types: 8-K, 10-Q, 10-K
Since: 2025-10-12

Fetching submissions for CIK 0000789019...
  Downloading 10-Q from 2025-10-29 (accession: 0001193125-25-256321)...
    Ingested: MICROSOFT CORP 10-Q (source_id=1)

Ingestion complete:
  Total filings found: 15
  New filings ingested: 15

Extracting signals from 15 sources...
  MICROSOFT CORP 10-Q (2025-10-29): 11 signals
  ALPHABET INC 10-Q (2025-10-28): 8 signals
  ...

Extraction complete: 143 total signals

Report generated: reports/weekly_report.md
```

## Usage

### Individual Commands

**1. Ingest SEC Filings**

Download filings from SEC EDGAR:

```bash
python -m aistreet sec-ingest --forms 8-K,10-Q,10-K --since 90d
```

Options:
- `--forms`: Comma-separated form types (default: 8-K,10-Q,10-K)
- `--since`: Lookback period like "7d", "90d", or ISO date "2025-01-01"
- `--universe`: Path to universe file (default: data/universe.txt)

**What it does**: Fetches filing metadata from SEC, downloads primary documents, converts HTML to text, stores in SQLite.

**2. Extract Signals**

Analyze downloaded filings for compute demand signals:

```bash
python -m aistreet extract
```

**What it does**: Reads all text files, applies keyword pattern matching, extracts sentences mentioning compute demand, stores structured signals in database. Can be run multiple times safely (deletes old signals before re-extracting).

**3. Generate Report**

Create a markdown summary:

```bash
python -m aistreet report --since 90d
```

Options:
- `--since`: Filter signals by filing date (default: 7d)

**What it does**: Queries database for signals, generates `reports/weekly_report.md` with statistics, top 10 signals, and company breakdowns.

**4. Generate Calendar View**

Create an interactive HTML calendar showing past filings and upcoming expected earnings:

```bash
python -m aistreet calendar --since 90d
```

Options:
- `--since`: Lookback period for historical filings (default: 90d)
- `--output`: Output path for HTML file (default: reports/calendar.html)

**What it does**:
- Creates a visual timeline of filings organized by week
- Shows signals color-coded by constraint type
- Predicts upcoming earnings dates based on fiscal calendars
- Open `reports/calendar.html` in your browser for an at-a-glance view

**5. Show Upcoming Filings**

Quickly view predicted upcoming earnings dates in the CLI:

```bash
python -m aistreet upcoming --days 60
```

Options:
- `--days`: Number of days to look ahead (default: 60)

**What it does**: Shows a table of expected filings based on company fiscal calendars. Useful for quick checks of who's reporting this week/month.

**6. Run Full Pipeline**

All three steps in one command:

```bash
python -m aistreet run-all --since 90d
```

**When to use**: Weekly updates, initial setup, or after modifying the universe.

## Modifying the Universe

The universe of companies is defined in `data/universe.txt`. Each line contains one CIK (Central Index Key).

### Current Universe

The default universe focuses on compute-intensive companies:

- Microsoft (0000789019)
- Alphabet (0001652044)
- Amazon (0001018724)
- Meta Platforms (0001326801)
- NVIDIA (0000788784)
- AMD (0000002488)
- Broadcom (0001730168)
- Arista Networks (0001144215)
- Equinix (0001101239)
- Digital Realty (0001297996)
- Vertiv (0001665907)

### Adding Companies

1. Find the company's CIK at https://www.sec.gov/edgar/searchedgar/companysearch.html
2. Add the 10-digit CIK to `data/universe.txt` (one per line)
3. Re-run the pipeline:

```bash
python -m aistreet run_all --since 30d
```

### Example: Adding Tesla

```bash
# Find Tesla's CIK: 0001318605
echo "0001318605" >> data/universe.txt

# Run pipeline
python -m aistreet run_all --since 90d
```

## Data Model

### Sources Table

Stores metadata about ingested filings:

- `source_id`: Primary key
- `company`: Company name
- `cik`: Central Index Key
- `form_type`: Form type (8-K, 10-Q, 10-K)
- `filing_date`: Filing date (ISO format)
- `source_type`: Always "filing" in v1
- `title`: Form type + accession number
- `url`: SEC Archives URL
- `text_path`: Path to local text file
- `created_at`: Timestamp

### Signals Table

Stores extracted compute demand signals:

- `signal_id`: Primary key
- `source_id`: Foreign key to sources
- `quote`: Verbatim sentence from filing
- `demand_direction`: up | down | flat | unclear
- `segment`: training | inference | general
- `constraint_type`: power | chips | networking | capacity | other | none
- `pricing`: up | down | stable | unclear
- `time_horizon`: now | next_qtr | 6_12mo | 12mo_plus | unclear
- `confidence`: 0.0 to 1.0
- `notes`: Traceability hints (e.g., sentence index)
- `created_at`: Timestamp

## Project Structure

```
.
├── aistreet/
│   ├── cli.py                  # CLI commands
│   ├── config.py               # Configuration
│   ├── db/
│   │   ├── models.py           # Database schema
│   │   └── repository.py       # Database operations
│   ├── sec/
│   │   ├── client.py           # SEC API client
│   │   ├── parser.py           # HTML to text conversion
│   │   └── ingest.py           # Filing ingestion
│   ├── extraction/
│   │   ├── base.py             # Extractor interface
│   │   ├── keywords.py         # Keyword patterns
│   │   └── rule_based.py       # Rule-based extractor
│   └── reporting/
│       └── generator.py        # Report generation
├── data/
│   ├── universe.txt            # Company CIKs
│   ├── raw/sec/                # Raw filings
│   └── signals.db              # SQLite database
├── reports/
│   └── weekly_report.md        # Generated report
└── tests/
    ├── test_extractor.py       # Extractor tests
    └── test_report.py          # Report tests
```

## Running Tests

```bash
pytest tests/ -v
```

Or run individual test files:

```bash
pytest tests/test_extractor.py -v
pytest tests/test_report.py -v
```

## Compliance

This pipeline complies with SEC fair access guidelines:

- Uses descriptive User-Agent header
- Respects rate limits (max 10 requests/second)
- Only accesses official SEC APIs (no scraping)

## Extending the Pipeline

### Adding LLM-Based Extraction

The extractor interface is designed for easy extension. To add an LLM-based extractor:

1. Create a new class inheriting from `aistreet.extraction.base.Extractor`
2. Implement the `extract(text: str, source_id: int) -> list[Signal]` method
3. Update `aistreet/cli.py` to use your new extractor

Example:

```python
from aistreet.extraction.base import Extractor
from aistreet.db.repository import Signal

class LLMExtractor(Extractor):
    def extract(self, text: str, source_id: int) -> list[Signal]:
        # Your LLM logic here
        pass
```

### Adding New Signal Attributes

1. Update the database schema in `aistreet/db/models.py`
2. Update the `Signal` class in `aistreet/db/repository.py`
3. Update extractors to populate new fields
4. Update report generation as needed

## License

Private - AI Street Newsletter

## Contact

For questions or feedback, contact: newsletter@aistreet.example.com
