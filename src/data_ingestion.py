from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"

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


def load_csvs() -> dict[str, pd.DataFrame]:
    """Load the 10 provided Day 1 CSV datasets and print schema snapshots."""
    loaded: dict[str, pd.DataFrame] = {}
    missing_files = [name for name in DAY1_DATASETS if not (RAW_DIR / name).exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing required Day 1 datasets: {missing_files}")

    for file_name in DAY1_DATASETS:
        file_path = RAW_DIR / file_name
        df = pd.read_csv(file_path)
        loaded[file_name] = df

        print(f"\n--- {file_name} ---")
        print("Shape:", df.shape)
        print("Dtypes:\n", df.dtypes)
        print("Head:\n", df.head())
        print("Missing values:\n", df.isna().sum())
        print("Duplicate rows:", int(df.duplicated().sum()))

    return loaded


def explore_fund_master(fund_master: pd.DataFrame) -> dict[str, object]:
    """Explore key AMFI fund master dimensions."""
    risk_column = (
        "risk_grade"
        if "risk_grade" in fund_master.columns
        else "risk_category"
        if "risk_category" in fund_master.columns
        else None
    )

    summary = {
        "unique_fund_houses": int(fund_master["fund_house"].nunique())
        if "fund_house" in fund_master.columns
        else 0,
        "unique_categories": int(fund_master["category"].nunique())
        if "category" in fund_master.columns
        else 0,
        "unique_sub_categories": int(fund_master["sub_category"].nunique())
        if "sub_category" in fund_master.columns
        else 0,
        "unique_risk_grades": int(fund_master[risk_column].nunique())
        if risk_column
        else 0,
    }

    print("\n=== Fund Master Exploration ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    return summary  # pyright: ignore[reportReturnType]


def validate_amfi_codes(
    fund_master: pd.DataFrame, nav_history: pd.DataFrame
) -> dict[str, object]:
    """Confirm every AMFI code in fund_master exists in nav_history."""
    fund_codes = set(fund_master["amfi_code"].dropna().astype(int).tolist())
    nav_codes = set(nav_history["amfi_code"].dropna().astype(int).tolist())

    missing_in_nav = sorted(fund_codes - nav_codes)
    extra_in_nav = sorted(nav_codes - fund_codes)

    validation = {
        "fund_master_code_count": len(fund_codes),
        "nav_history_code_count": len(nav_codes),
        "missing_in_nav_count": len(missing_in_nav),
        "extra_in_nav_count": len(extra_in_nav),
        "missing_in_nav_sample": missing_in_nav[:10],
        "extra_in_nav_sample": extra_in_nav[:10],
    }

    print("\n=== AMFI Code Validation ===")
    for key, value in validation.items():
        print(f"{key}: {value}")
    return validation


def write_day1_quality_summary(
    loaded: dict[str, pd.DataFrame],
    fund_summary: dict[str, object],
    code_validation: dict[str, object],
) -> Path:
    """Write short Day 1 data quality report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "day1_data_quality_summary.md"

    lines = [
        "# Day 1 Data Quality Summary",
        "",
        "## Dataset ingestion status",
        f"- Total required datasets loaded: {len(loaded)}/10",
    ]

    for name, df in loaded.items():
        lines.append(
            f"- {name}: rows={df.shape[0]}, cols={df.shape[1]}, "
            f"missing_cells={int(df.isna().sum().sum())}, duplicates={int(df.duplicated().sum())}"
        )

    lines += [
        "",
        "## Fund master exploration",
        f"- Unique fund houses: {fund_summary['unique_fund_houses']}",
        f"- Unique categories: {fund_summary['unique_categories']}",
        f"- Unique sub-categories: {fund_summary['unique_sub_categories']}",
        f"- Unique risk grades: {fund_summary['unique_risk_grades']}",
        "",
        "## AMFI code validation",
        f"- Fund master unique AMFI codes: {code_validation['fund_master_code_count']}",
        f"- NAV history unique AMFI codes: {code_validation['nav_history_code_count']}",
        f"- Missing from nav_history: {code_validation['missing_in_nav_count']}",
        f"- Extra in nav_history: {code_validation['extra_in_nav_count']}",
        f"- Missing sample: {code_validation['missing_in_nav_sample']}",
        f"- Extra sample: {code_validation['extra_in_nav_sample']}",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSaved quality summary: {report_path}")
    return report_path


def main() -> None:
    loaded = load_csvs()
    fund_summary = explore_fund_master(loaded["01_fund_master.csv"])
    code_validation = validate_amfi_codes(
        loaded["01_fund_master.csv"], loaded["02_nav_history.csv"]
    )
    write_day1_quality_summary(loaded, fund_summary, code_validation)


if __name__ == "__main__":
    main()
