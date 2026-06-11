"""
Day 2 ETL - Data Cleaning & Validation Module
==============================================
Clean, validate, and standardize the 10 raw mutual fund datasets.
Generates processed CSV outputs and creates SQLite database schema.

This module:
- Cleans each of the 10 raw datasets (fund master, NAV, AUM, SIP, transactions, etc.)
- Standardizes data types, handles missing values, and removes duplicates
- Expands NAV history to include all trading days (forward-fill missing dates)
- Saves cleaned datasets to the processed directory
- Generates SQLite database schema for data warehousing
- Creates data dictionary and query templates
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DB_PATH = PROJECT_ROOT / "bluestock_mf.db"
SCHEMA_SQL_PATH = PROJECT_ROOT / "schema.sql"
QUERIES_SQL_PATH = PROJECT_ROOT / "queries.sql"
DATA_DICT_PATH = PROJECT_ROOT / "data_dictionary.md"

DAY1_DATASETS = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]


def ensure_processed_dir() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def clean_fund_master(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["launch_date"] = pd.to_datetime(cleaned["launch_date"], errors="coerce")
    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    cleaned = cleaned.assign(
        fund_house=cleaned["fund_house"].astype(str).str.strip(),
        scheme_name=cleaned["scheme_name"].astype(str).str.strip(),
        category=cleaned["category"].astype(str).str.strip(),
        sub_category=cleaned["sub_category"].astype(str).str.strip(),
        plan=cleaned["plan"].astype(str).str.strip(),
        benchmark=cleaned["benchmark"].astype(str).str.strip(),
        fund_manager=cleaned["fund_manager"].astype(str).str.strip(),
        risk_category=cleaned["risk_category"].astype(str).str.strip(),
    )
    return cleaned


def clean_nav_history(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned = cleaned.dropna(subset=["date"])
    cleaned = cleaned[cleaned["nav"] > 0]
    cleaned = cleaned.drop_duplicates(subset=["amfi_code", "date"]).sort_values([
        "amfi_code",
        "date",
    ])

    records: list[pd.DataFrame] = []
    for code, group in cleaned.groupby("amfi_code", sort=False):
        group = group.set_index("date").sort_index()
        full_dates = pd.date_range(group.index.min(), group.index.max(), freq="D")
        expanded = group.reindex(full_dates)
        expanded["amfi_code"] = code
        expanded["nav"] = expanded["nav"].ffill()
        expanded = expanded.reset_index().rename(columns={"index": "date"})
        records.append(expanded)

    return pd.concat(records, ignore_index=True).dropna(subset=["nav"])


def clean_aum_by_fund_house(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    cleaned = cleaned.assign(
        fund_house=cleaned["fund_house"].astype(str).str.strip(),
    )
    return cleaned


def clean_monthly_sip_inflows(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["month"] = pd.to_datetime(cleaned["month"].astype(str) + "-01", errors="coerce")
    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    return cleaned


def clean_category_inflows(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["month"] = pd.to_datetime(cleaned["month"].astype(str) + "-01", errors="coerce")
    cleaned = cleaned.assign(category=cleaned["category"].astype(str).str.strip())
    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    return cleaned


def clean_industry_folio_count(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["month"] = pd.to_datetime(cleaned["month"].astype(str) + "-01", errors="coerce")
    return cleaned.drop_duplicates().reset_index(drop=True)


def clean_scheme_performance(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    cleaned = cleaned.assign(
        scheme_name=cleaned["scheme_name"].astype(str).str.strip(),
        fund_house=cleaned["fund_house"].astype(str).str.strip(),
        category=cleaned["category"].astype(str).str.strip(),
        plan=cleaned["plan"].astype(str).str.strip(),
        risk_grade=cleaned["risk_grade"].astype(str).str.strip(),
    )

    cleaned["expense_ratio_flag"] = (~cleaned["expense_ratio_pct"].between(0.1, 2.5)).astype(int)
    numeric_returns = cleaned[["return_1yr_pct", "return_3yr_pct", "return_5yr_pct"]].apply(
        lambda col: pd.to_numeric(col, errors="coerce")
    )
    cleaned["return_flag"] = (~numeric_returns.notna().all(axis=1)).astype(int)
    return cleaned


def clean_investor_transactions(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["transaction_date"] = pd.to_datetime(cleaned["transaction_date"], errors="coerce")
    cleaned = cleaned.dropna(subset=["transaction_date"])
    cleaned["transaction_type"] = (
        cleaned["transaction_type"]
        .astype(str)
        .str.strip()
        .str.upper()
        .replace({"LUMPSUM": "LUMPSUM", "SIP": "SIP", "REDEMPTION": "REDEMPTION"})
    )
    cleaned = cleaned[cleaned["amount_inr"] > 0]
    cleaned = cleaned.assign(
        state=cleaned["state"].astype(str).str.strip(),
        city=cleaned["city"].astype(str).str.strip(),
        city_tier=cleaned["city_tier"].astype(str).str.strip(),
        age_group=cleaned["age_group"].astype(str).str.strip(),
        gender=cleaned["gender"].astype(str).str.strip(),
        payment_mode=cleaned["payment_mode"].astype(str).str.strip(),
        kyc_status=cleaned["kyc_status"].astype(str).str.strip(),
    )
    cleaned["transaction_id"] = (
        "TX_" + cleaned.reset_index().index.astype(str).str.zfill(6)
    )
    return cleaned.drop_duplicates().reset_index(drop=True)


def clean_portfolio_holdings(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["portfolio_date"] = pd.to_datetime(cleaned["portfolio_date"], errors="coerce")
    cleaned = cleaned.assign(
        stock_symbol=cleaned["stock_symbol"].astype(str).str.strip(),
        stock_name=cleaned["stock_name"].astype(str).str.strip(),
        sector=cleaned["sector"].astype(str).str.strip(),
    )
    return cleaned.drop_duplicates().reset_index(drop=True)


def clean_benchmark_indices(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned = cleaned.assign(index_name=cleaned["index_name"].astype(str).str.strip())
    return cleaned.drop_duplicates().reset_index(drop=True)


CLEANING_FUNCTIONS = {
    "01_fund_master.csv": clean_fund_master,
    "02_nav_history.csv": clean_nav_history,
    "03_aum_by_fund_house.csv": clean_aum_by_fund_house,
    "04_monthly_sip_inflows.csv": clean_monthly_sip_inflows,
    "05_category_inflows.csv": clean_category_inflows,
    "06_industry_folio_count.csv": clean_industry_folio_count,
    "07_scheme_performance.csv": clean_scheme_performance,
    "08_investor_transactions.csv": clean_investor_transactions,
    "09_portfolio_holdings.csv": clean_portfolio_holdings,
    "10_benchmark_indices.csv": clean_benchmark_indices,
}


def save_cleaned_csv(name: str, df: pd.DataFrame) -> Path:
    path = PROCESSED_DIR / name
    df.to_csv(path, index=False)
    return path


def write_schema_sql() -> None:
    content = """
-- SQLite schema for Day 2 star schema and supporting tables

CREATE TABLE IF NOT EXISTS dim_date (
    date TEXT PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    day INTEGER,
    month_name TEXT,
    week_of_year INTEGER
);

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT,
    scheme_name TEXT,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date TEXT,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount INTEGER,
    min_lumpsum_amount INTEGER,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code INTEGER,
    date TEXT,
    nav REAL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id TEXT PRIMARY KEY,
    investor_id TEXT,
    transaction_date TEXT,
    amfi_code INTEGER,
    transaction_type TEXT,
    amount_inr INTEGER,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date)
);

CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    expense_ratio_flag INTEGER,
    return_flag INTEGER,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_aum_by_fund_house (
    date TEXT,
    fund_house TEXT,
    aum_lakh_crore REAL,
    aum_crore INTEGER,
    num_schemes INTEGER
);

CREATE TABLE IF NOT EXISTS fact_monthly_sip_inflows (
    month TEXT,
    sip_inflow_crore INTEGER,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

CREATE TABLE IF NOT EXISTS fact_category_inflows (
    month TEXT,
    category TEXT,
    net_inflow_crore REAL
);

CREATE TABLE IF NOT EXISTS fact_industry_folio_count (
    month TEXT,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

CREATE TABLE IF NOT EXISTS fact_portfolio_holdings (
    amfi_code INTEGER,
    stock_symbol TEXT,
    stock_name TEXT,
    sector TEXT,
    weight_pct REAL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_benchmark_indices (
    date TEXT,
    index_name TEXT,
    close_value REAL
);

CREATE INDEX IF NOT EXISTS idx_fact_nav_date ON fact_nav(date);
CREATE INDEX IF NOT EXISTS idx_fact_transactions_date ON fact_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_fact_transactions_state ON fact_transactions(state);
CREATE INDEX IF NOT EXISTS idx_fact_performance_amfi ON fact_performance(amfi_code);
"""
    SCHEMA_SQL_PATH.write_text(content.strip() + "\n", encoding="utf-8")


def write_queries_sql() -> None:
    content = """
-- 1. Top 5 funds by AUM
SELECT
    f.amfi_code,
    f.scheme_name,
    p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month across all funds
SELECT
    strftime('%Y-%m', date) AS month,
    ROUND(AVG(nav), 2) AS avg_nav
FROM fact_nav
GROUP BY month
ORDER BY month;

-- 3. SIP YoY growth by month
SELECT
    month,
    yoy_growth_pct
FROM fact_monthly_sip_inflows
ORDER BY month;

-- 4. Transaction volume by state
SELECT
    state,
    COUNT(*) AS transaction_count,
    SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- 5. Funds with expense ratio under 1%
SELECT
    amfi_code,
    scheme_name,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- 6. Top 10 funds by 5-year return
SELECT
    f.amfi_code,
    f.scheme_name,
    p.return_5yr_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.return_5yr_pct DESC
LIMIT 10;

-- 7. Average AUM by fund house
SELECT
    fund_house,
    ROUND(AVG(aum_crore), 2) AS avg_aum_crore
FROM fact_aum_by_fund_house
GROUP BY fund_house
ORDER BY avg_aum_crore DESC;

-- 8. Scheme count by category
SELECT
    category,
    COUNT(*) AS scheme_count
FROM dim_fund
GROUP BY category
ORDER BY scheme_count DESC;

-- 9. Total SIP and Redemption amount by transaction month
SELECT
    strftime('%Y-%m', transaction_date) AS month,
    SUM(CASE WHEN transaction_type = 'SIP' THEN amount_inr ELSE 0 END) AS sip_amount,
    SUM(CASE WHEN transaction_type = 'REDEMPTION' THEN amount_inr ELSE 0 END) AS redemption_amount
FROM fact_transactions
GROUP BY month
ORDER BY month;

-- 10. Top sectors by portfolio weight
SELECT
    sector,
    ROUND(SUM(weight_pct), 2) AS total_weight_pct
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY total_weight_pct DESC
LIMIT 5;
"""
    QUERIES_SQL_PATH.write_text(content.strip() + "\n", encoding="utf-8")


def write_data_dictionary() -> None:
    content = """
# Data Dictionary

## 01_fund_master.csv
- amfi_code: Numeric ID for each mutual fund scheme.
- fund_house: Asset management company name.
- scheme_name: Full mutual fund scheme name.
- category: Asset class category (e.g. Equity, Debt).
- sub_category: Scheme sub-segment (e.g. Large Cap, Small Cap).
- plan: Regular or Direct investment plan.
- launch_date: Fund launch date.
- benchmark: Reference benchmark index.
- expense_ratio_pct: Annual expense ratio percentage.
- exit_load_pct: Exit load percentage for early redemption.
- min_sip_amount: Minimum SIP amount in INR.
- min_lumpsum_amount: Minimum lump sum investment in INR.
- fund_manager: Name of the scheme fund manager.
- risk_category: Risk category label.
- sebi_category_code: SEBI classification code.

## 02_nav_history.csv
- amfi_code: Fund scheme ID.
- date: Daily NAV date.
- nav: Net asset value per unit.

## 03_aum_by_fund_house.csv
- date: Reporting date.
- fund_house: Mutual fund company name.
- aum_lakh_crore: Assets under management in lakh crore.
- aum_crore: Assets under management in crore.
- num_schemes: Number of schemes reported.

## 04_monthly_sip_inflows.csv
- month: Month of SIP inflows.
- sip_inflow_crore: Total monthly SIP inflow in crore INR.
- active_sip_accounts_crore: Active SIP accounts in crore.
- new_sip_accounts_lakh: New SIP accounts in lakh.
- sip_aum_lakh_crore: SIP AUM in lakh crore.
- yoy_growth_pct: Year-over-year growth rate for the month.

## 05_category_inflows.csv
- month: Month of category inflow data.
- category: Fund category.
- net_inflow_crore: Net inflow amount in crore INR.

## 06_industry_folio_count.csv
- month: Month of folio count data.
- total_folios_crore: Total folios in crore.
- equity_folios_crore: Equity folios in crore.
- debt_folios_crore: Debt folios in crore.
- hybrid_folios_crore: Hybrid folios in crore.
- others_folios_crore: Other folios in crore.

## 07_scheme_performance.csv
- amfi_code: Fund scheme ID.
- scheme_name: Scheme name.
- fund_house: Asset management company.
- category: Scheme category.
- plan: Regular or Direct plan.
- return_1yr_pct: 1-year return percentage.
- return_3yr_pct: 3-year return percentage.
- return_5yr_pct: 5-year return percentage.
- benchmark_3yr_pct: Benchmark 3-year return percentage.
- alpha: Risk-adjusted performance alpha.
- beta: Market sensitivity beta.
- sharpe_ratio: Sharpe ratio.
- sortino_ratio: Sortino ratio.
- std_dev_ann_pct: Annualized standard deviation.
- max_drawdown_pct: Maximum 3-year drawdown.
- aum_crore: AUM in crore.
- expense_ratio_pct: Expense ratio percentage.
- morningstar_rating: Morningstar rating value.
- risk_grade: Risk grade label.
- expense_ratio_flag: Flag when expense ratio is outside 0.1-2.5%.
- return_flag: Flag for invalid return values.

## 08_investor_transactions.csv
- transaction_id: Synthetic unique transaction identifier.
- investor_id: Investor identifier.
- transaction_date: Transaction date.
- amfi_code: Fund scheme ID.
- transaction_type: Transaction type (SIP, LUMPSUM, REDEMPTION).
- amount_inr: Transaction amount in INR.
- state: Investor state.
- city: Investor city.
- city_tier: City tier category.
- age_group: Investor age group.
- gender: Investor gender.
- annual_income_lakh: Annual income in lakh INR.
- payment_mode: Payment mode.
- kyc_status: KYC verification status.

## 09_portfolio_holdings.csv
- amfi_code: Fund scheme ID.
- stock_symbol: Stock ticker symbol.
- stock_name: Stock name.
- sector: Industry sector.
- weight_pct: Holding weight percentage.
- market_value_cr: Market value in crore.
- current_price_inr: Current stock price in INR.
- portfolio_date: Portfolio reporting date.

## 10_benchmark_indices.csv
- date: Index closing date.
- index_name: Benchmark index identifier.
- close_value: Index close value.
"""
    DATA_DICT_PATH.write_text(content.strip() + "\n", encoding="utf-8")


def build_date_dimension(df: pd.DataFrame) -> pd.DataFrame:
    dates = pd.to_datetime(df["date"].dropna().unique())
    result = pd.DataFrame({"date": dates})
    result = result.assign(
        year=result["date"].dt.year,
        month=result["date"].dt.month,
        quarter=result["date"].dt.quarter,
        day=result["date"].dt.day,
        month_name=result["date"].dt.strftime("%B"),
        week_of_year=result["date"].dt.isocalendar().week,
    )
    result["date"] = result["date"].dt.strftime("%Y-%m-%d")
    return result.sort_values("date").drop_duplicates().reset_index(drop=True)


def load_to_sqlite(cleaned_data: dict[str, pd.DataFrame]) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    engine = create_engine(f"sqlite:///{DB_PATH}")
    schema_sql = SCHEMA_SQL_PATH.read_text(encoding="utf-8")
    statements = [
        stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()
    ]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))

    # ensure date dimension exists from all date sources
    date_frames: list[pd.DataFrame] = []
    for name, df in cleaned_data.items():
        if "date" in df.columns:
            date_frames.append(df[["date"]].drop_duplicates())
        if name == "04_monthly_sip_inflows.csv" and "month" in df.columns:
            date_frames.append(df.rename(columns={"month": "date"})[["date"]])
        if name == "05_category_inflows.csv" and "month" in df.columns:
            date_frames.append(df.rename(columns={"month": "date"})[["date"]])
        if name == "06_industry_folio_count.csv" and "month" in df.columns:
            date_frames.append(df.rename(columns={"month": "date"})[["date"]])
        if name == "09_portfolio_holdings.csv" and "portfolio_date" in df.columns:
            date_frames.append(df.rename(columns={"portfolio_date": "date"})[["date"]])

    if date_frames:
        df_dates = pd.concat(date_frames, ignore_index=True).drop_duplicates().reset_index(drop=True)
        df_dates = build_date_dimension(df_dates)
        df_dates.to_sql("dim_date", engine, if_exists="append", index=False)

    # Load dim_fund first from fund master
    fund_master = cleaned_data["01_fund_master.csv"].copy()
    fund_master.to_sql("dim_fund", engine, if_exists="append", index=False)

    table_map = {
        "02_nav_history.csv": "fact_nav",
        "03_aum_by_fund_house.csv": "fact_aum_by_fund_house",
        "04_monthly_sip_inflows.csv": "fact_monthly_sip_inflows",
        "05_category_inflows.csv": "fact_category_inflows",
        "06_industry_folio_count.csv": "fact_industry_folio_count",
        "07_scheme_performance.csv": "fact_performance",
        "08_investor_transactions.csv": "fact_transactions",
        "09_portfolio_holdings.csv": "fact_portfolio_holdings",
        "10_benchmark_indices.csv": "fact_benchmark_indices",
    }

    fact_performance_columns = [
        "amfi_code",
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
        "risk_grade",
        "expense_ratio_flag",
        "return_flag",
    ]

    for name, table_name in table_map.items():
        df_to_load = cleaned_data[name].copy()
        if table_name == "fact_performance":
            df_to_load = df_to_load[[c for c in fact_performance_columns if c in df_to_load.columns]]
        df_to_load.to_sql(table_name, engine, if_exists="append", index=False)


def main() -> None:
    ensure_processed_dir()
    cleaned_data: dict[str, pd.DataFrame] = {}
    for file_name in DAY1_DATASETS:
        raw_path = RAW_DIR / file_name
        if not raw_path.exists():
            raise FileNotFoundError(f"Missing raw source file: {raw_path}")

        df = pd.read_csv(raw_path)
        cleaner = CLEANING_FUNCTIONS[file_name]
        cleaned = cleaner(df)
        cleaned_data[file_name] = cleaned
        output_path = save_cleaned_csv(file_name, cleaned)
        print(f"Saved cleaned dataset: {output_path} ({cleaned.shape[0]} rows, {cleaned.shape[1]} cols)")

    write_schema_sql()
    write_queries_sql()
    write_data_dictionary()
    load_to_sqlite(cleaned_data)
    print(f"SQLite database created: {DB_PATH}")
    print(f"Schema file written: {SCHEMA_SQL_PATH}")
    print(f"Queries file written: {QUERIES_SQL_PATH}")
    print(f"Data dictionary written: {DATA_DICT_PATH}")


if __name__ == "__main__":
    main()
