"""Command-line interface for AI Street pipeline."""

from pathlib import Path
from typing import Optional

import click

from aistreet.config import SUPPORTED_FORMS, UNIVERSE_PATH
from aistreet.db.models import init_db
from aistreet.db.repository import (
    delete_signals_for_source,
    get_all_sources,
    insert_signal,
)
from aistreet.extraction.rule_based import RuleBasedExtractor
from aistreet.reporting.calendar import generate_and_save_calendar
from aistreet.reporting.earnings_predictor import predict_upcoming_filings
from aistreet.reporting.generator import generate_and_save_report, generate_and_save_html_report, generate_and_save_index
from aistreet.sec.ingest import ingest_filings, parse_lookback_period


@click.group()
def cli():
    """AI Street - SEC compute demand signal extraction pipeline."""
    pass


@cli.command()
@click.option(
    "--forms",
    default="8-K,10-Q,10-K",
    help="Comma-separated list of form types to ingest",
)
@click.option(
    "--since",
    default="7d",
    help="Lookback period (e.g., 7d, 30d) or ISO date (yyyy-mm-dd)",
)
@click.option(
    "--universe",
    type=click.Path(exists=True),
    default=str(UNIVERSE_PATH),
    help="Path to universe file (one CIK per line)",
)
def sec_ingest(forms: str, since: str, universe: str):
    """Ingest SEC filings for companies in universe."""
    # Initialize database
    init_db()

    # Parse form types
    form_types = {f.strip() for f in forms.split(",")}
    invalid = form_types - SUPPORTED_FORMS
    if invalid:
        click.echo(f"Error: Unsupported form types: {invalid}", err=True)
        return

    # Parse lookback period
    since_date = parse_lookback_period(since)

    # Load CIKs from universe file
    universe_path = Path(universe)
    ciks = [line.strip() for line in universe_path.read_text().splitlines() if line.strip()]

    click.echo(f"Ingesting filings for {len(ciks)} companies...")
    click.echo(f"Form types: {', '.join(sorted(form_types))}")
    click.echo(f"Since: {since_date}")
    click.echo("")

    # Run ingestion
    total_found, total_ingested = ingest_filings(ciks, form_types, since_date)

    click.echo("")
    click.echo(f"Ingestion complete:")
    click.echo(f"  Total filings found: {total_found}")
    click.echo(f"  New filings ingested: {total_ingested}")


@cli.command()
def extract():
    """Extract signals from all ingested sources."""
    # Initialize database
    init_db()

    # Get all sources
    sources = get_all_sources()

    if not sources:
        click.echo("No sources found in database. Run 'sec_ingest' first.")
        return

    click.echo(f"Extracting signals from {len(sources)} sources...")

    extractor = RuleBasedExtractor()
    total_signals = 0

    for source in sources:
        # Read text file
        from aistreet.config import DATA_DIR
        text_path = DATA_DIR / source.text_path
        if not text_path.exists():
            click.echo(f"Warning: Text file not found: {text_path}", err=True)
            continue

        text = text_path.read_text(encoding="utf-8")

        # Delete existing signals for this source (repeatability)
        deleted = delete_signals_for_source(source.source_id)

        # Extract signals
        signals = extractor.extract(text, source.source_id)

        # Insert signals
        for signal in signals:
            insert_signal(signal)

        total_signals += len(signals)

        if signals:
            click.echo(
                f"  {source.company} {source.form_type} ({source.filing_date}): "
                f"{len(signals)} signals"
            )

    click.echo("")
    click.echo(f"Extraction complete: {total_signals} total signals")


@cli.command()
@click.option(
    "--since",
    default="7d",
    help="Filter signals by filing date (e.g., 7d, 30d) or ISO date",
)
def report(since: str):
    """Generate markdown and HTML reports of signals."""
    # Initialize database
    init_db()

    # Parse lookback period
    since_date = parse_lookback_period(since)

    click.echo(f"Generating reports for filings since {since_date}...")

    # Generate and save markdown report
    report_path = generate_and_save_report(since_date)
    click.echo(f"Markdown report: {report_path}")

    # Generate and save HTML report
    from aistreet.config import DATA_DIR
    html_path = DATA_DIR.parent / "reports" / "report.html"
    html_report_path = generate_and_save_html_report(str(html_path), since_date)
    click.echo(f"HTML report: {html_report_path}")

    # Generate and save index page (uses all signals, not filtered)
    index_path = DATA_DIR.parent / "docs" / "index.html"
    index_html_path = generate_and_save_index(str(index_path))
    click.echo(f"Index page: {index_html_path}")


@cli.command()
@click.option(
    "--since",
    default="90d",
    help="Lookback period (e.g., 7d, 90d) or ISO date",
)
@click.option(
    "--output",
    default="reports/calendar.html",
    help="Output path for HTML calendar",
)
def calendar(since: str, output: str):
    """Generate an HTML calendar view of filings and signals."""
    # Initialize database
    init_db()

    # Parse lookback period
    since_date = parse_lookback_period(since)

    click.echo(f"Generating calendar for filings since {since_date}...")

    # Generate and save calendar
    from aistreet.config import DATA_DIR
    output_path = DATA_DIR.parent / output
    calendar_path = generate_and_save_calendar(str(output_path), since_date)

    click.echo(f"Calendar generated: {calendar_path}")
    click.echo(f"\nOpen in browser: file://{output_path.absolute()}")


@cli.command()
@click.option(
    "--days",
    default=60,
    help="Number of days to look ahead (default: 60)",
)
def upcoming(days: int):
    """Show predicted upcoming earnings filings."""
    click.echo(f"Predicting filings for the next {days} days...\n")

    predictions = predict_upcoming_filings(days_ahead=days)

    if not predictions:
        click.echo("No upcoming filings predicted in this timeframe.")
        return

    click.echo(f"Found {len(predictions)} expected filings:\n")
    click.echo(f"{'Company':<40} {'Form':<8} {'Expected Date':<15} {'Quarter End'}")
    click.echo("-" * 80)

    from datetime import datetime

    for filing in predictions:
        date_obj = datetime.strptime(filing["expected_date"], "%Y-%m-%d")
        days_until = (date_obj - datetime.now()).days

        time_desc = ""
        if days_until <= 7:
            time_desc = f"({days_until}d)"
        elif days_until <= 14:
            time_desc = "(next week)"
        else:
            weeks = days_until // 7
            time_desc = f"({weeks}w)"

        click.echo(
            f"{filing['company']:<40} {filing['form_type']:<8} "
            f"{filing['expected_date']:<15} {filing['quarter_end']} {time_desc}"
        )

    click.echo("\nNote: Dates are estimates based on fiscal calendars (±5 days)")


@cli.command()
@click.option(
    "--since",
    default="7d",
    help="Lookback period (e.g., 7d, 30d) or ISO date",
)
@click.option(
    "--universe",
    type=click.Path(exists=True),
    default=str(UNIVERSE_PATH),
    help="Path to universe file",
)
def run_all(since: str, universe: str):
    """Run the full pipeline: ingest, extract, and report."""
    click.echo("=" * 60)
    click.echo("AI Street Pipeline - Full Run")
    click.echo("=" * 60)
    click.echo("")

    # Step 1: Ingest
    click.echo("Step 1: Ingesting SEC filings...")
    click.echo("-" * 60)
    ctx = click.get_current_context()
    ctx.invoke(sec_ingest, forms="8-K,10-Q,10-K", since=since, universe=universe)

    click.echo("")
    click.echo("")

    # Step 2: Extract
    click.echo("Step 2: Extracting signals...")
    click.echo("-" * 60)
    ctx.invoke(extract)

    click.echo("")
    click.echo("")

    # Step 3: Report
    click.echo("Step 3: Generating report...")
    click.echo("-" * 60)
    ctx.invoke(report, since=since)

    click.echo("")
    click.echo("=" * 60)
    click.echo("Pipeline complete!")
    click.echo("=" * 60)


if __name__ == "__main__":
    cli()
