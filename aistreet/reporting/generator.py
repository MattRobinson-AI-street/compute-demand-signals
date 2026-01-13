"""Report generation for compute demand signals."""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from aistreet.config import WEEKLY_REPORT_PATH
from aistreet.db.repository import get_signal_stats, get_signals_with_sources


def generate_report(since_date: Optional[str] = None) -> str:
    """
    Generate a markdown report of compute demand signals.

    Args:
        since_date: Optional ISO date to filter signals (based on filing_date)

    Returns:
        Markdown report content
    """
    # Fetch signals with source data
    signals = get_signals_with_sources(since_date=since_date)

    # Get statistics
    stats = get_signal_stats()

    # Build report
    lines = []
    lines.append("# AI Street Compute Demand Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    if since_date:
        lines.append(f"**Period:** Filings from {since_date} onwards")
    else:
        lines.append("**Period:** All filings")
    lines.append("")

    # Summary statistics
    lines.append("## Summary Statistics")
    lines.append("")
    lines.append(f"**Total Signals:** {len(signals)}")
    lines.append("")

    # Demand direction breakdown
    lines.append("### Signals by Demand Direction")
    lines.append("")
    lines.append("| Direction | Count |")
    lines.append("|-----------|-------|")
    for direction in ["up", "down", "flat", "unclear"]:
        count = stats["demand_direction"].get(direction, 0)
        lines.append(f"| {direction} | {count} |")
    lines.append("")

    # Constraint breakdown
    lines.append("### Signals by Constraint Type")
    lines.append("")
    lines.append("| Constraint | Count |")
    lines.append("|------------|-------|")
    for constraint in ["power", "chips", "networking", "capacity", "other", "none"]:
        count = stats["constraint_type"].get(constraint, 0)
        lines.append(f"| {constraint} | {count} |")
    lines.append("")

    # Top 10 newest signals
    lines.append("## Top 10 Recent Signals")
    lines.append("")

    top_signals = signals[:10]
    for sig in top_signals:
        lines.append(f"### {sig['company']} - {sig['form_type']} ({sig['filing_date']})")
        lines.append("")
        lines.append(f"**Direction:** {sig['demand_direction']} | "
                    f"**Segment:** {sig['segment']} | "
                    f"**Constraint:** {sig['constraint_type']}")
        lines.append("")
        lines.append(f"**Pricing:** {sig['pricing']} | "
                    f"**Time Horizon:** {sig['time_horizon']} | "
                    f"**Confidence:** {sig['confidence']:.2f}")
        lines.append("")
        lines.append(f"> {sig['quote']}")
        lines.append("")
        lines.append(f"*Source:* [{sig['title']}]({sig['url']})")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Signals grouped by company
    lines.append("## Signals by Company")
    lines.append("")

    # Group signals by company
    by_company = defaultdict(list)
    for sig in signals:
        by_company[sig["company"]].append(sig)

    for company in sorted(by_company.keys()):
        company_signals = by_company[company]
        lines.append(f"### {company} ({len(company_signals)} signals)")
        lines.append("")

        for sig in company_signals[:5]:  # Limit to 5 per company
            lines.append(f"**{sig['form_type']}** ({sig['filing_date']}) - "
                        f"{sig['demand_direction']} / {sig['segment']} / "
                        f"{sig['constraint_type']}")
            lines.append("")
            lines.append(f"> {sig['quote'][:200]}{'...' if len(sig['quote']) > 200 else ''}")
            lines.append("")

        if len(company_signals) > 5:
            lines.append(f"*...and {len(company_signals) - 5} more*")
            lines.append("")

        lines.append("")

    return "\n".join(lines)


def save_report(content: str, path: Optional[str] = None) -> None:
    """
    Save report to file.

    Args:
        content: Report markdown content
        path: Optional custom path (defaults to WEEKLY_REPORT_PATH)
    """
    if path is None:
        path = WEEKLY_REPORT_PATH

    # Ensure directory exists
    WEEKLY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Write report
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Report saved to {path}")


def generate_and_save_report(since_date: Optional[str] = None) -> str:
    """
    Generate and save a report.

    Args:
        since_date: Optional ISO date to filter signals

    Returns:
        Path to saved report
    """
    content = generate_report(since_date)
    save_report(content)
    return str(WEEKLY_REPORT_PATH)


def generate_html_report(since_date: Optional[str] = None) -> str:
    """
    Generate an HTML version of the report.

    Args:
        since_date: Optional ISO date to filter signals

    Returns:
        HTML report content
    """
    # Fetch signals with source data
    signals = get_signals_with_sources(since_date=since_date)

    # Get statistics
    stats = get_signal_stats()

    # Group signals by company
    by_company = defaultdict(list)
    for sig in signals:
        by_company[sig["company"]].append(sig)

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compute Demand Report - AI Street</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0e27;
            color: #e4e4e7;
            line-height: 1.6;
        }}

        nav {{
            background: #18181b;
            border-bottom: 1px solid #27272a;
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .nav-content {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .nav-brand {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #fff;
            text-decoration: none;
        }}

        .nav-links {{
            display: flex;
            gap: 2rem;
            list-style: none;
        }}

        .nav-links a {{
            color: #a1a1aa;
            text-decoration: none;
            transition: color 0.2s;
            font-weight: 500;
        }}

        .nav-links a:hover {{
            color: #fff;
        }}

        .nav-links a.active {{
            color: #3b82f6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .header {{
            margin-bottom: 3rem;
        }}

        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #fff;
            margin-bottom: 0.5rem;
        }}

        .meta {{
            color: #a1a1aa;
            font-size: 0.95rem;
        }}

        .stats-section {{
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 3rem;
        }}

        h2 {{
            font-size: 1.75rem;
            font-weight: 600;
            color: #fff;
            margin-bottom: 1.5rem;
        }}

        h3 {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #fff;
            margin-bottom: 1rem;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .stat-item {{
            background: #1f1f23;
            padding: 1.25rem;
            border-radius: 8px;
        }}

        .stat-label {{
            color: #71717a;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}

        .stat-value {{
            color: #fff;
            font-size: 2rem;
            font-weight: 700;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}

        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid #27272a;
        }}

        th {{
            color: #71717a;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 500;
        }}

        td {{
            color: #d4d4d8;
        }}

        .signal-card {{
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: border-color 0.2s;
        }}

        .signal-card:hover {{
            border-color: #3f3f46;
        }}

        .signal-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 1rem;
        }}

        .company-name {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #fff;
        }}

        .filing-date {{
            color: #a1a1aa;
            font-size: 0.9rem;
        }}

        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }}

        .badge-up {{
            background: #14532d;
            color: #86efac;
        }}

        .badge-down {{
            background: #7f1d1d;
            color: #fca5a5;
        }}

        .badge-constraint {{
            background: #422006;
            color: #fbbf24;
        }}

        .badge-confidence {{
            background: #1e3a8a;
            color: #93c5fd;
        }}

        .quote {{
            color: #d4d4d8;
            font-style: italic;
            margin: 1rem 0;
            padding-left: 1rem;
            border-left: 3px solid #3f3f46;
            line-height: 1.7;
        }}

        .sec-link {{
            color: #3b82f6;
            text-decoration: none;
            font-size: 0.9rem;
            transition: color 0.2s;
        }}

        .sec-link:hover {{
            color: #60a5fa;
            text-decoration: underline;
        }}

        .company-section {{
            margin-bottom: 3rem;
        }}

        .signal-list {{
            margin-top: 1rem;
        }}

        .signal-item {{
            background: #1f1f23;
            border-left: 3px solid #3b82f6;
            padding: 1rem;
            margin-bottom: 0.75rem;
            border-radius: 4px;
        }}

        .signal-item.power {{
            border-left-color: #ef4444;
        }}

        .signal-item.chips {{
            border-left-color: #8b5cf6;
        }}

        .signal-item.networking {{
            border-left-color: #06b6d4;
        }}

        .signal-item.capacity {{
            border-left-color: #f59e0b;
        }}

        .more-signals {{
            color: #71717a;
            font-style: italic;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}

        footer {{
            text-align: center;
            padding: 2rem;
            color: #71717a;
            font-size: 0.9rem;
            border-top: 1px solid #27272a;
            margin-top: 4rem;
        }}
    </style>
</head>
<body>
    <nav>
        <div class="nav-content">
            <a href="index.html" class="nav-brand">AI Street</a>
            <ul class="nav-links">
                <li><a href="index.html">Home</a></li>
                <li><a href="calendar.html">Calendar</a></li>
                <li><a href="report.html" class="active">Report</a></li>
            </ul>
        </div>
    </nav>

    <div class="container">
        <div class="header">
            <h1>Compute Demand Report</h1>
            <p class="meta">
                Generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}<br>
                Period: {"Filings from " + since_date + " onwards" if since_date else "All filings"}
            </p>
        </div>

        <div class="stats-section">
            <h2>Summary Statistics</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">Total Signals</div>
                    <div class="stat-value">{len(signals)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Companies</div>
                    <div class="stat-value">{len(by_company)}</div>
                </div>
            </div>

            <h3>Signals by Demand Direction</h3>
            <table>
                <thead>
                    <tr>
                        <th>Direction</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
"""

    for direction in ["up", "down", "flat", "unclear"]:
        count = stats["demand_direction"].get(direction, 0)
        html += f"""                    <tr>
                        <td>{direction.capitalize()}</td>
                        <td>{count}</td>
                    </tr>
"""

    html += """                </tbody>
            </table>

            <h3 style="margin-top: 2rem;">Signals by Constraint Type</h3>
            <table>
                <thead>
                    <tr>
                        <th>Constraint</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
"""

    for constraint in ["power", "chips", "networking", "capacity", "other", "none"]:
        count = stats["constraint_type"].get(constraint, 0)
        html += f"""                    <tr>
                        <td>{constraint.capitalize()}</td>
                        <td>{count}</td>
                    </tr>
"""

    html += """                </tbody>
            </table>
        </div>

        <h2>Top 10 Recent Signals</h2>
"""

    # Top 10 signals
    for sig in signals[:10]:
        demand_class = f"badge-{sig['demand_direction']}" if sig['demand_direction'] in ['up', 'down'] else ''
        constraint_class = sig['constraint_type'] if sig['constraint_type'] != 'none' else ''

        html += f"""
        <div class="signal-card">
            <div class="signal-header">
                <div>
                    <div class="company-name">{sig['company']}</div>
                    <div class="filing-date">{sig['form_type']} - {sig['filing_date']}</div>
                </div>
            </div>
            <div>
                <span class="badge {demand_class}">Demand {sig['demand_direction']}</span>
                <span class="badge">{sig['segment'].capitalize()}</span>
"""

        if sig['constraint_type'] != 'none':
            html += f"""                <span class="badge badge-constraint">{sig['constraint_type'].capitalize()}</span>
"""

        html += f"""                <span class="badge badge-confidence">{sig['confidence']:.0%} Confidence</span>
            </div>
            <div class="quote">"{sig['quote']}"</div>
            <a href="{sig['url']}" target="_blank" rel="noopener" class="sec-link">View on SEC →</a>
        </div>
"""

    html += """
        <h2 style="margin-top: 3rem;">Signals by Company</h2>
"""

    # Group by company
    for company in sorted(by_company.keys()):
        company_signals = by_company[company]
        html += f"""
        <div class="company-section">
            <h3>{company} ({len(company_signals)} signals)</h3>
            <div class="signal-list">
"""

        for sig in company_signals[:5]:
            constraint_class = sig['constraint_type'] if sig['constraint_type'] != 'none' else ''
            html += f"""                <div class="signal-item {constraint_class}">
                    <div style="margin-bottom: 0.5rem;">
                        <span class="badge badge-{sig['demand_direction'] if sig['demand_direction'] in ['up', 'down'] else 'default'}">{sig['form_type']}</span>
                        <span style="color: #a1a1aa; font-size: 0.85rem;">{sig['filing_date']} - {sig['demand_direction']} / {sig['segment']} / {sig['constraint_type']}</span>
                    </div>
                    <div class="quote" style="margin: 0; padding-left: 0; border-left: none;">"{sig['quote'][:200]}{'...' if len(sig['quote']) > 200 else ''}"</div>
                </div>
"""

        if len(company_signals) > 5:
            html += f"""                <div class="more-signals">...and {len(company_signals) - 5} more signals</div>
"""

        html += """            </div>
        </div>
"""

    html += """    </div>

    <footer>
        <p>Data sourced from SEC EDGAR | Generated automatically via rule-based extraction</p>
        <p style="margin-top: 0.5rem;">AI Street Compute Demand Intelligence</p>
    </footer>
</body>
</html>
"""

    return html


def save_html_report(content: str, path: str) -> None:
    """Save HTML report to file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"HTML report saved to {path}")


def generate_and_save_html_report(output_path: str, since_date: Optional[str] = None) -> str:
    """Generate and save HTML report."""
    content = generate_html_report(since_date)
    save_html_report(content, output_path)
    return output_path
