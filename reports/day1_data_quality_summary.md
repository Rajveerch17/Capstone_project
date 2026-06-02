# Day 1 Data Quality Summary

## Dataset ingestion status
- Total required datasets loaded: 10/10
- 01_fund_master.csv: rows=40, cols=15, missing_cells=0, duplicates=0
- 02_nav_history.csv: rows=46000, cols=3, missing_cells=0, duplicates=0
- 03_aum_by_fund_house.csv: rows=90, cols=5, missing_cells=0, duplicates=0
- 04_monthly_sip_inflows.csv: rows=48, cols=6, missing_cells=12, duplicates=0
- 05_category_inflows.csv: rows=144, cols=3, missing_cells=0, duplicates=0
- 06_industry_folio_count.csv: rows=21, cols=6, missing_cells=0, duplicates=0
- 07_scheme_performance.csv: rows=40, cols=19, missing_cells=0, duplicates=0
- 08_investor_transactions.csv: rows=32778, cols=13, missing_cells=0, duplicates=0
- 09_portfolio_holdings.csv: rows=322, cols=8, missing_cells=0, duplicates=0
- 10_benchmark_indices.csv: rows=8050, cols=3, missing_cells=0, duplicates=0

## Fund master exploration
- Unique fund houses: 10
- Unique categories: 2
- Unique sub-categories: 12
- Unique risk grades: 5

## AMFI code validation
- Fund master unique AMFI codes: 40
- NAV history unique AMFI codes: 40
- Missing from nav_history: 0
- Extra in nav_history: 0
- Missing sample: []
- Extra sample: []