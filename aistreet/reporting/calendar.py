"""Calendar view generator for compute demand signals."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from aistreet.db.repository import get_signals_with_sources
from aistreet.reporting.earnings_predictor import predict_upcoming_filings


def generate_calendar_html(since_date: Optional[str] = None) -> str:
    """
    Generate an HTML calendar view of filings and signals.

    Args:
        since_date: Optional ISO date to filter signals (defaults to 90 days ago)

    Returns:
        HTML content for calendar view
    """
    # Default to 90 days if not specified
    if since_date is None:
        since_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    # Fetch signals with source data
    signals = get_signals_with_sources(since_date=since_date)

    # Group by filing date and company
    filings_by_date = defaultdict(lambda: defaultdict(list))
    for sig in signals:
        filing_date = sig['filing_date']
        company = sig['company']
        filings_by_date[filing_date][company].append(sig)

    # Get unique companies
    all_companies = set()
    for date_data in filings_by_date.values():
        all_companies.update(date_data.keys())

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compute Demand Calendar</title>
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
            padding: 2rem;
        }}

        .header {{
            max-width: 1400px;
            margin: 0 auto 2rem;
        }}

        h1 {{
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #fff;
        }}

        .subtitle {{
            color: #a1a1aa;
            font-size: 0.95rem;
        }}

        .stats {{
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
        }}

        .stat {{
            display: flex;
            flex-direction: column;
        }}

        .stat-label {{
            color: #71717a;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .stat-value {{
            color: #fff;
            font-size: 1.5rem;
            font-weight: 600;
        }}

        .timeline {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .week {{
            margin-bottom: 2rem;
        }}

        .week-header {{
            font-size: 0.85rem;
            color: #71717a;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #27272a;
        }}

        .day {{
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 8px;
            padding: 1.25rem;
            margin-bottom: 0.75rem;
            transition: border-color 0.2s;
        }}

        .day:hover {{
            border-color: #3f3f46;
        }}

        .day-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}

        .date {{
            font-weight: 600;
            font-size: 1.1rem;
            color: #fff;
        }}

        .day-stats {{
            display: flex;
            gap: 1rem;
            font-size: 0.85rem;
            color: #a1a1aa;
        }}

        .filings {{
            display: grid;
            gap: 0.75rem;
        }}

        .filing {{
            background: #1f1f23;
            border-left: 3px solid #3b82f6;
            padding: 1rem;
            border-radius: 4px;
        }}

        .filing.capacity {{
            border-left-color: #f59e0b;
        }}

        .filing.power {{
            border-left-color: #ef4444;
        }}

        .filing.chips {{
            border-left-color: #8b5cf6;
        }}

        .filing.networking {{
            border-left-color: #06b6d4;
        }}

        .filing-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 0.75rem;
        }}

        .company-name {{
            font-weight: 600;
            font-size: 1rem;
            color: #fff;
        }}

        .form-type {{
            background: #27272a;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
            color: #a1a1aa;
        }}

        .signals {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}

        .signal {{
            font-size: 0.9rem;
            color: #d4d4d8;
            padding-left: 1rem;
            border-left: 2px solid #3f3f46;
        }}

        .signal-meta {{
            display: flex;
            gap: 0.75rem;
            margin-bottom: 0.25rem;
            font-size: 0.8rem;
        }}

        .badge {{
            padding: 0.15rem 0.5rem;
            border-radius: 3px;
            font-size: 0.75rem;
            font-weight: 500;
        }}

        .badge.demand-up {{
            background: #14532d;
            color: #86efac;
        }}

        .badge.demand-down {{
            background: #7f1d1d;
            color: #fca5a5;
        }}

        .badge.constraint {{
            background: #422006;
            color: #fbbf24;
        }}

        .badge.confidence {{
            background: #1e3a8a;
            color: #93c5fd;
        }}

        .quote {{
            color: #a1a1aa;
            font-size: 0.85rem;
            line-height: 1.5;
            margin-top: 0.5rem;
        }}

        .empty-state {{
            text-align: center;
            padding: 4rem 2rem;
            color: #71717a;
        }}

        .legend {{
            max-width: 1400px;
            margin: 2rem auto 0;
            padding: 1.5rem;
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 8px;
        }}

        .legend-title {{
            font-size: 0.85rem;
            color: #71717a;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
        }}

        .legend-items {{
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .legend-color {{
            width: 20px;
            height: 3px;
            border-radius: 2px;
        }}

        .legend-label {{
            font-size: 0.85rem;
            color: #a1a1aa;
        }}

        .upcoming-section {{
            max-width: 1400px;
            margin: 2rem auto;
            padding: 1.5rem;
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 8px;
        }}

        .section-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #fff;
            margin-bottom: 1rem;
        }}

        .upcoming-filing {{
            background: #1f1f23;
            border-left: 3px solid #6366f1;
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 0.75rem;
        }}

        .upcoming-filing:hover {{
            background: #27272a;
        }}

        .upcoming-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}

        .upcoming-date {{
            font-size: 0.9rem;
            color: #a1a1aa;
        }}

        .estimated-badge {{
            background: #1e3a8a;
            color: #93c5fd;
            padding: 0.15rem 0.5rem;
            border-radius: 3px;
            font-size: 0.75rem;
            font-weight: 500;
        }}

        .divider {{
            height: 1px;
            background: #27272a;
            max-width: 1400px;
            margin: 3rem auto;
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

        .sec-link {{
            color: #3b82f6;
            text-decoration: none;
            font-size: 0.8rem;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            transition: color 0.2s;
        }}

        .sec-link:hover {{
            color: #60a5fa;
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <nav>
        <div class="nav-content">
            <a href="index.html" class="nav-brand">AI Street</a>
            <ul class="nav-links">
                <li><a href="index.html">Home</a></li>
                <li><a href="calendar.html" class="active">Calendar</a></li>
                <li><a href="report.html">Report</a></li>
            </ul>
        </div>
    </nav>

    <div class="header">
        <h1>Compute Demand Calendar</h1>
        <p class="subtitle">Generated {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}</p>
        <div class="stats">
            <div class="stat">
                <span class="stat-label">Total Signals</span>
                <span class="stat-value">{len(signals)}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Companies</span>
                <span class="stat-value">{len(all_companies)}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Filings</span>
                <span class="stat-value">{len(filings_by_date)}</span>
            </div>
        </div>
    </div>
"""

    # Get upcoming filings predictions
    upcoming = predict_upcoming_filings(days_ahead=60)

    if upcoming:
        html += """
    <div class="upcoming-section">
        <div class="section-title">📅 Expected Filings (Next 60 Days)</div>
"""
        for filing in upcoming:
            date_obj = datetime.strptime(filing["expected_date"], "%Y-%m-%d")
            days_until = (date_obj - datetime.now()).days
            date_label = date_obj.strftime("%A, %B %d, %Y")

            time_desc = ""
            if days_until == 0:
                time_desc = "Today"
            elif days_until == 1:
                time_desc = "Tomorrow"
            elif days_until <= 7:
                time_desc = f"In {days_until} days"
            elif days_until <= 14:
                time_desc = "Next week"
            else:
                weeks = days_until // 7
                time_desc = f"In {weeks} weeks"

            html += f"""
        <div class="upcoming-filing">
            <div class="upcoming-header">
                <div class="company-name">{filing['company']}</div>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <span class="form-type">{filing['form_type']}</span>
                    <span class="estimated-badge">estimated</span>
                </div>
            </div>
            <div class="upcoming-date">{date_label} ({time_desc})</div>
            <div class="upcoming-date" style="font-size: 0.8rem; margin-top: 0.25rem;">Quarter ending: {filing['quarter_end']}</div>
        </div>
"""

        html += """
    </div>
"""

    # Add divider
    if upcoming:
        html += """
    <div class="divider"></div>
"""

    html += """
    <div class="timeline">
"""

    # Sort dates in reverse chronological order
    sorted_dates = sorted(filings_by_date.keys(), reverse=True)

    if not sorted_dates:
        html += """
        <div class="empty-state">
            <p>No filings found in the specified period.</p>
            <p style="margin-top: 0.5rem; font-size: 0.9rem;">Try running: python -m aistreet run-all --since 90d</p>
        </div>
"""
    else:
        # Group by week
        current_week = None
        for filing_date in sorted_dates:
            date_obj = datetime.strptime(filing_date, "%Y-%m-%d")
            week_start = date_obj - timedelta(days=date_obj.weekday())
            week_key = week_start.strftime("%Y-%m-%d")

            if week_key != current_week:
                if current_week is not None:
                    html += "    </div>\n"  # Close previous week
                current_week = week_key
                week_label = week_start.strftime("%B %d, %Y")
                html += f"""        <div class="week">
            <div class="week-header">Week of {week_label}</div>
"""

            # Create day card
            day_label = date_obj.strftime("%A, %B %d")
            companies_data = filings_by_date[filing_date]
            total_signals = sum(len(sigs) for sigs in companies_data.values())

            html += f"""            <div class="day">
                <div class="day-header">
                    <div class="date">{day_label}</div>
                    <div class="day-stats">
                        <span>{len(companies_data)} {'company' if len(companies_data) == 1 else 'companies'}</span>
                        <span>•</span>
                        <span>{total_signals} {'signal' if total_signals == 1 else 'signals'}</span>
                    </div>
                </div>
                <div class="filings">
"""

            # Add each company's filing
            for company in sorted(companies_data.keys()):
                company_signals = companies_data[company]
                form_type = company_signals[0]['form_type']
                filing_url = company_signals[0]['url']

                # Determine primary constraint for color coding
                constraint_types = [s['constraint_type'] for s in company_signals]
                primary_constraint = max(set(constraint_types), key=constraint_types.count)
                constraint_class = primary_constraint if primary_constraint != 'none' else ''

                html += f"""                    <div class="filing {constraint_class}">
                        <div class="filing-header">
                            <div class="company-name">{company}</div>
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <div class="form-type">{form_type}</div>
                                <a href="{filing_url}" target="_blank" rel="noopener" class="sec-link">View on SEC →</a>
                            </div>
                        </div>
                        <div class="signals">
"""

                # Show up to 3 most confident signals
                top_signals = sorted(company_signals, key=lambda x: x['confidence'], reverse=True)[:3]

                for sig in top_signals:
                    demand_class = f"demand-{sig['demand_direction']}" if sig['demand_direction'] in ['up', 'down'] else ''
                    constraint_badge = f"<span class='badge constraint'>{sig['constraint_type']}</span>" if sig['constraint_type'] != 'none' else ''

                    html += f"""                            <div class="signal">
                                <div class="signal-meta">
                                    <span class="badge {demand_class}">demand {sig['demand_direction']}</span>
                                    {constraint_badge}
                                    <span class="badge confidence">{sig['confidence']:.0%}</span>
                                </div>
                                <div class="quote">"{sig['quote'][:200]}{'...' if len(sig['quote']) > 200 else ''}"</div>
                            </div>
"""

                if len(company_signals) > 3:
                    html += f"""                            <div class="signal" style="opacity: 0.6; font-size: 0.85rem;">
                                +{len(company_signals) - 3} more signals
                            </div>
"""

                html += """                        </div>
                    </div>
"""

            html += """                </div>
            </div>
"""

        html += "    </div>\n"  # Close last week

    html += """    </div>

    <div class="legend">
        <div class="legend-title">Constraint Types</div>
        <div class="legend-items">
            <div class="legend-item">
                <div class="legend-color" style="background: #3b82f6;"></div>
                <span class="legend-label">No constraint</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #f59e0b;"></div>
                <span class="legend-label">Capacity</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ef4444;"></div>
                <span class="legend-label">Power</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #8b5cf6;"></div>
                <span class="legend-label">Chips</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #06b6d4;"></div>
                <span class="legend-label">Networking</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

    return html


def save_calendar_html(content: str, path: str) -> None:
    """Save calendar HTML to file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Calendar saved to {path}")


def generate_and_save_calendar(output_path: str, since_date: Optional[str] = None) -> str:
    """Generate and save calendar HTML."""
    content = generate_calendar_html(since_date)
    save_calendar_html(content, output_path)
    return output_path
