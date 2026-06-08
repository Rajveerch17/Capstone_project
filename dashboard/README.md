# Bluestock Dashboard Deliverable

This folder contains the generated Day 5 dashboard outputs for the mutual fund analytics project.

## Files
- `bluestock_dashboard.html` — interactive multi-section dashboard report showing industry overview, fund performance, investor analytics, and SIP/market trends.
- `bluestock_dashboard.pdf` — multi-page PDF report exported from the generated dashboard charts.
- `page1_kpis.png`, `page1_aum_trend.png`, `page1_aum_by_amc.png` — Page 1 visuals.
- `page2_return_vs_risk.png`, `page2_scorecard_table.png`, `page2_nav_vs_benchmark.png` — Page 2 visuals.
- `page3_amount_by_state.png`, `page3_transaction_type_split.png`, `page3_avg_sip_by_age_group.png`, `page3_transaction_volume.png` — Page 3 visuals.
- `page4_sip_nifty_trend.png`, `page4_category_inflow_heatmap.png`, `page4_top5_categories_fy25.png` — Page 4 visuals.

## Run
```bash
python src/day5_dashboard.py
```

This will regenerate the dashboard HTML/PDF and all PNG exports using the cleaned `data/processed` tables.
