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
|   `-- live_nav_fetch.py
|-- reports/
|   `-- day1_data_quality_summary.md
|-- notebooks/          # analysis notebooks (future days)
|-- sql/                # SQL scripts (future days)
|-- dashboard/          # dashboard app (future days)
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
