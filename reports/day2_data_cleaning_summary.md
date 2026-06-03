# Day 2 Data Cleaning + SQL Database Summary

## Overview
- Completed Day 2 deliverables for data cleaning, SQLite schema design, database loading, query generation, and data dictionary documentation.
- Built cleaned datasets from the raw Day 1 files and stored them in `data/processed/`.
- Created an SQLite database at `bluestock_mf.db` and schema script at `schema.sql`.
- Added analytical SQL queries in `queries.sql` and documented columns in `data_dictionary.md`.

## Cleaned datasets and row counts
- `01_fund_master.csv`: 40 rows, 15 cols
- `02_nav_history.csv`: 64320 rows, 3 cols
- `03_aum_by_fund_house.csv`: 90 rows, 5 cols
- `04_monthly_sip_inflows.csv`: 48 rows, 6 cols
- `05_category_inflows.csv`: 144 rows, 3 cols
- `06_industry_folio_count.csv`: 21 rows, 6 cols
- `07_scheme_performance.csv`: 40 rows, 21 cols
- `08_investor_transactions.csv`: 32778 rows, 14 cols
- `09_portfolio_holdings.csv`: 322 rows, 8 cols
- `10_benchmark_indices.csv`: 8050 rows, 3 cols

## Data cleaning actions
- Parsed `transaction_date`, `date`, `launch_date`, and monthly period fields to datetime.
- Standardized transaction types in `08_investor_transactions.csv` and validated positive `amount_inr` values.
- Forward-filled missing NAV values for each fund in `02_nav_history.csv` to cover gaps in the daily time series.
- Flagged outlier expense ratios in `07_scheme_performance.csv` outside the expected range of 0.1%–2.5%.
- Removed duplicate rows and normalized string fields where appropriate.

## SQL database and schema
- Created `dim_date`, `dim_fund`, `fact_nav`, `fact_transactions`, `fact_performance`, and supporting fact tables.
- Loaded all cleaned datasets into `bluestock_mf.db` using Python and SQLAlchemy.
- Created indexes to support analytical queries on date and state filters.

## Analytical queries included
1. Top 5 funds by AUM.
2. Average NAV per month.
3. SIP YoY growth by month.
4. Transaction volume by state.
5. Funds with expense ratio under 1%.
6. Top 10 funds by 5-year return.
7. Average AUM by fund house.
8. Scheme count by category.
9. Total SIP and redemption amount by month.
10. Top portfolio sectors by weight.

## Deliverables generated
- `data/processed/` cleaned CSVs
- `bluestock_mf.db`
- `schema.sql`
- `queries.sql`
- `data_dictionary.md`
- `reports/day2_data_cleaning_summary.md`

## Notes
- The `02_nav_history.csv` cleaned dataset includes a forward-filled NAV time series for every fund across its available date range.
- `08_investor_transactions.csv` includes a new synthetic `transaction_id` column for unique transaction records.
- `data_dictionary.md` documents all columns, data types, and business definitions for the Day 2 datasets.
