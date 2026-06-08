# Mutual Fund Analytics Project

Day 1 implementation for project setup and data ingestion (ETL) using mutual fund datasets and live NAV pulls from `mfapi.in`.

## Project Structure

```text
Capstone_project/
|-- data/
|   |-- raw/            # input CSV files + fetched NAV CSV files
|   `-- processed/      # cleaned/derived outputs (future days)
|-- src/
|   |-- data_ingestion.py
|   |-- live_nav_fetch.py
|   `-- day3_eda.py
|-- reports/
|   |-- day1_data_quality_summary.md
|   |-- day2_data_cleaning_summary.md
|   |-- day3_eda_summary.md
|   `-- day5_dashboard_summary.md
|-- notebooks/          # analysis notebooks and Day 3 EDA deliverables
|-- sql/                # SQL scripts (future days)
|-- dashboard/          # dashboard app and Day 5 deliverables
|-- requirements.txt
`-- README.md
```

## Day 1 Deliverables Completed

- Project folder structure created.
- Dependencies listed in `requirements.txt`.
- All 10 provided CSV datasets loaded and profiled in `src/data_ingestion.py`.
- Live NAV fetch implemented in `src/live_nav_fetch.py` for:
  - `125497` (HDFC Top 100 Direct)
  - `119551` (SBI Bluechip)
  - `120503` (ICICI Bluechip)
  - `118632` (Nippon Large Cap)
  - `119092` (Axis Bluechip)
  - `120841` (Kotak Bluechip)
- Fund master exploration completed (fund houses, categories, sub-categories, risk grades).
- AMFI code validation completed (`fund_master` vs `nav_history`).
- Data quality summary generated at `reports/day1_data_quality_summary.md`.

## Day 2 Deliverables Completed

- Cleaned all 10 Day 1 raw CSV datasets and saved outputs in `data/processed/`.
- Built `src/day2_data_cleaning.py` to automate data cleaning and SQLite loading.
- Created SQLite database `bluestock_mf.db` and schema file `schema.sql`.
- Added analytical SQL queries in `queries.sql`.
- Documented the schema and data definitions in `data_dictionary.md`.
- Generated Day 2 report summary at `reports/day2_data_cleaning_summary.md`.

## Day 3 Deliverables Completed

- Built `src/day3_eda.py` to perform exploratory data analysis and export visualizations.
- Created Day 3 notebook deliverables at `notebooks/EDA_Analysis.ipynb` and `notebooks/EDA_Analysis_executed.ipynb`.
- Generated Day 3 summary report at `reports/day3_eda_summary.md`.
- Exported charts to `notebooks/plots/` including NAV trends, AUM growth, SIP trend, demographic distributions, geographic SIP analysis, folio growth, fund return correlations, and sector allocation.

## Day 4 Deliverables Completed

- Added `src/day4_fund_performance.py` to compute daily returns, CAGR, Sharpe, Sortino, alpha/beta, maximum drawdown, tracking error, and a fund scorecard.
- Created `notebooks/Performance_Analytics.ipynb` for the Day 4 analytics workflow.
- Generated `fund_scorecard.csv`, `alpha_beta.csv`, `performance_comparison.csv`, and `notebooks/plots/benchmark_comparison_chart.png`.

## Day 5 Deliverables Completed

- Built `src/day5_dashboard.py` to generate the Day 5 dashboard and export charts.
- Created `dashboard/bluestock_dashboard.html` and `dashboard/bluestock_dashboard.pdf` for the final report.
- Added `dashboard/README.md` to document the dashboard deliverable and export files.
- Generated PNG export files for all four Day 5 dashboard pages in `dashboard/`.

## Run Day 2 pipeline

```bash
python src/day2_data_cleaning.py
```

## Run Day 3 EDA

```bash
python src/day3_eda.py
```

## Run Day 4 Analytics

```bash
python src/day4_fund_performance.py
```

## Run Day 5 Dashboard

```bash
python src/day5_dashboard.py
```

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
```

## Run

1) Load and validate provided datasets + generate quality summary:

```bash
python src/data_ingestion.py
```

2) Fetch live NAV history and save into `data/raw/`:

```bash
python src/live_nav_fetch.py
```

## Notes

- Live API calls may occasionally fail with transient HTTP errors; the fetch script includes retry logic.
- The Day 1 commit message target is: `Day 1: Data ingestion complete`.
