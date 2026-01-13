"""Configuration and constants for AI Street."""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw" / "sec"
DB_PATH = DATA_DIR / "signals.db"
UNIVERSE_PATH = DATA_DIR / "universe.txt"

# Reports directory
REPORTS_DIR = PROJECT_ROOT / "reports"
WEEKLY_REPORT_PATH = REPORTS_DIR / "weekly_report.md"

# SEC API configuration
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
SEC_ARCHIVES_BASE_URL = "https://www.sec.gov/Archives/edgar/data"
SEC_USER_AGENT = "AI Street Newsletter newsletter@aistreet.example.com"
SEC_RATE_LIMIT_DELAY = 0.11  # Just over 100ms to stay under 10 req/sec

# Supported form types
SUPPORTED_FORMS = {"8-K", "10-Q", "10-K"}

# Signal extraction enums
DEMAND_DIRECTIONS = {"up", "down", "flat", "unclear"}
SEGMENTS = {"training", "inference", "general"}
CONSTRAINTS = {"power", "chips", "networking", "capacity", "other", "none"}
PRICING_TRENDS = {"up", "down", "stable", "unclear"}
TIME_HORIZONS = {"now", "next_qtr", "6_12mo", "12mo_plus", "unclear"}
