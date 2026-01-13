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

    # Get statistics (filtered by same date range)
    stats = get_signal_stats(since_date=since_date)

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

    # Get statistics (filtered by same date range)
    stats = get_signal_stats(since_date=since_date)

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


def generate_index_html() -> str:
    """
    Generate the index.html homepage with current stats.

    Returns:
        HTML content for index page
    """
    # Get all signals (no date filter for homepage overview)
    all_signals = get_signals_with_sources()

    # Get unique companies and filings
    companies = set(sig['company'] for sig in all_signals)
    filings = set((sig['company'], sig['filing_date'], sig['form_type']) for sig in all_signals)

    # Get the most recent filing date
    if all_signals:
        latest_date = max(sig['filing_date'] for sig in all_signals)
        latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
        last_updated = latest_dt.strftime('%b %d')
        last_updated_year = latest_dt.strftime('%Y')
    else:
        last_updated = "N/A"
        last_updated_year = ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Street - Compute Demand Intelligence</title>
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
            min-height: 100vh;
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

        .hero {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 4rem 2rem;
            text-align: center;
        }}

        h1 {{
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #fff;
            line-height: 1.2;
        }}

        .subtitle {{
            font-size: 1.25rem;
            color: #a1a1aa;
            margin-bottom: 3rem;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
        }}

        .stats-grid {{
            max-width: 1400px;
            margin: 0 auto 4rem;
            padding: 0 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }}

        .stat-card {{
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 12px;
            padding: 2rem;
            transition: border-color 0.2s;
        }}

        .stat-card:hover {{
            border-color: #3f3f46;
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
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}

        .stat-description {{
            color: #a1a1aa;
            font-size: 0.9rem;
        }}

        .cta-section {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem 4rem;
        }}

        .cta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
        }}

        .cta-card {{
            background: linear-gradient(135deg, #1e293b 0%, #18181b 100%);
            border: 1px solid #27272a;
            border-radius: 12px;
            padding: 2.5rem;
            text-decoration: none;
            transition: all 0.3s;
            display: block;
        }}

        .cta-card:hover {{
            border-color: #3b82f6;
            transform: translateY(-2px);
        }}

        .cta-icon {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}

        .cta-title {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #fff;
            margin-bottom: 0.75rem;
        }}

        .cta-description {{
            color: #a1a1aa;
            line-height: 1.6;
        }}

        .about-section {{
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 12px;
            padding: 2.5rem;
            margin-top: 3rem;
        }}

        .about-title {{
            font-size: 1.75rem;
            font-weight: 600;
            color: #fff;
            margin-bottom: 1rem;
        }}

        .about-content {{
            color: #d4d4d8;
            font-size: 1.05rem;
            line-height: 1.8;
            margin-bottom: 1.5rem;
        }}

        .companies-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}

        .company-badge {{
            background: #1f1f23;
            border: 1px solid #27272a;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            text-align: center;
            color: #d4d4d8;
            font-size: 0.9rem;
            font-weight: 500;
        }}

        footer {{
            text-align: center;
            padding: 3rem 2rem;
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
            <div class="nav-brand">AI Street</div>
            <ul class="nav-links">
                <li><a href="index.html">Home</a></li>
                <li><a href="calendar.html">Calendar</a></li>
                <li><a href="report.html">Report</a></li>
            </ul>
        </div>
    </nav>

    <div class="hero">
        <h1>Compute Demand Intelligence</h1>
        <p class="subtitle">
            Track AI infrastructure demand signals from SEC filings of major tech companies
        </p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Total Signals</div>
            <div class="stat-value">{len(all_signals)}</div>
            <div class="stat-description">Extracted from recent filings</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Companies Tracked</div>
            <div class="stat-value">{len(companies)}</div>
            <div class="stat-description">Major tech & infrastructure</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Recent Filings</div>
            <div class="stat-value">{len(filings)}</div>
            <div class="stat-description">10-Q, 10-K, 8-K forms</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Last Updated</div>
            <div class="stat-value">{last_updated}</div>
            <div class="stat-description">{last_updated_year}</div>
        </div>
    </div>

    <div class="cta-section">
        <div class="cta-grid">
            <a href="calendar.html" class="cta-card">
                <div class="cta-icon">📅</div>
                <div class="cta-title">Calendar View</div>
                <div class="cta-description">
                    Browse signals organized by filing date with visual indicators for constraint types and upcoming earnings predictions
                </div>
            </a>
            <a href="report.html" class="cta-card">
                <div class="cta-icon">📊</div>
                <div class="cta-title">Detailed Report</div>
                <div class="cta-description">
                    View comprehensive analysis with signal breakdowns, top insights, and company-by-company summaries with direct SEC links
                </div>
            </a>
        </div>
    </div>

    <div style="max-width: 1400px; margin: 0 auto; padding: 0 2rem;">
        <div class="about-section">
            <h2 class="about-title">What We Track</h2>
            <p class="about-content">
                This platform monitors SEC filings (10-Q, 10-K, 8-K) from major technology and infrastructure companies
                to extract signals about compute demand trends. We analyze statements about:
            </p>
            <ul style="color: #d4d4d8; font-size: 1.05rem; line-height: 2; list-style-position: inside;">
                <li><strong style="color: #fff;">Demand Direction:</strong> Is compute demand increasing, decreasing, or staying flat?</li>
                <li><strong style="color: #fff;">Infrastructure Constraints:</strong> Power, chip availability, networking, datacenter capacity</li>
                <li><strong style="color: #fff;">Infrastructure Segments:</strong> AI training, AI inference, general compute</li>
                <li><strong style="color: #fff;">Market Dynamics:</strong> Pricing trends and time horizons</li>
            </ul>

            <h3 style="font-size: 1.5rem; color: #fff; margin-top: 2rem; margin-bottom: 1rem;">Companies Monitored</h3>
            <div class="companies-grid">
                <div class="company-badge">Microsoft</div>
                <div class="company-badge">Alphabet</div>
                <div class="company-badge">Amazon</div>
                <div class="company-badge">Meta</div>
                <div class="company-badge">NVIDIA</div>
                <div class="company-badge">AMD</div>
                <div class="company-badge">Broadcom</div>
                <div class="company-badge">Arista Networks</div>
                <div class="company-badge">Equinix</div>
                <div class="company-badge">Digital Realty</div>
                <div class="company-badge">Vertiv</div>
            </div>
        </div>
    </div>

    <footer>
        <p>Data sourced from SEC EDGAR | Generated automatically via rule-based extraction</p>
        <p style="margin-top: 0.5rem;">AI Street Compute Demand Intelligence</p>
        <p style="margin-top: 0.5rem; font-size: 0.85rem;">Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
    </footer>
</body>
</html>
"""

    return html


def generate_and_save_index(output_path: str) -> str:
    """Generate and save index.html homepage."""
    content = generate_index_html()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Index page saved to {output_path}")
    return output_path
