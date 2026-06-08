# Day 5 Dashboard Summary

## Overview
- Completed Day 5 dashboard deliverables by generating a Power BI-style analytics report from the processed mutual fund dataset.
- Built `src/day5_dashboard.py` to create a 4-page dashboard with fund overview, performance analytics, investor behavior, and SIP market trend visualizations.
- Exported the dashboard as interactive HTML and a PDF report, plus page-specific PNG images for distribution.

## Key findings
- The dashboard consolidates fund master data, NAV performance, fund scorecard rankings, and benchmark performance into a single visual report.
- Fund performance pages compare growth, return distribution, and risk metrics while highlighting the strongest schemes based on scorecard rank and historical returns.
- Investor analytics pages surface SIP inflows, folio count trends, and key investor engagement patterns across categories and fund houses.
- The SIP market trends page visualizes monthly SIP inflows and category-level allocations, providing a snapshot of retail investment momentum.

## Deliverables generated
- `src/day5_dashboard.py`
- `dashboard/bluestock_dashboard.html`
- `dashboard/bluestock_dashboard.pdf`
- `dashboard/page1_overview.png`
- `dashboard/page2_fund_performance.png`
- `dashboard/page3_investor_analytics.png`
- `dashboard/page4_sip_market_trends.png`
- `dashboard/README.md`

## Notes
- The dashboard uses cleaned data from `data/processed/` and merges the fund scorecard with master fund details for richer analytics.
- Exported artifacts support both interactive review (`HTML`) and printable reporting (`PDF`).
- The summary file is placed in `reports/` to align Day 5 deliverables with the other daily project reports.
