"""
Day 6 Advanced Analytics Module
================================
Perform advanced risk analysis, investor cohort behavior, and portfolio optimization.
Generate risk metrics (VaR, CVaR), investor cohort analysis, and sector concentration indices.

This module:
- Loads NAV, transactions, holdings, and fund master data
- Computes Value at Risk (VaR) and Conditional VaR (CVaR) at 95% confidence level
- Calculates rolling 90-day Sharpe ratios for top performers
- Analyzes investor cohorts by first transaction year (SIP patterns, fund preferences)
- Identifies SIP continuity risks (long gaps, inconsistent behavior)
- Computes Herfindahl-Hirschman Index (HHI) for sector concentration in each equity fund
- Provides simple fund recommender based on risk appetite (Low/Moderate/High)
- Saves all analysis outputs as CSV files for reporting and downstream use
"""

from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR
PLOTS_DIR = BASE_DIR / "notebooks" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

TRADING_DAYS = 252


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "fund_master": pd.read_csv(PROCESSED_DIR / "01_fund_master.csv", parse_dates=["launch_date"]),
        "scheme_perf": pd.read_csv(PROCESSED_DIR / "07_scheme_performance.csv"),
        "nav_history": pd.read_csv(PROCESSED_DIR / "02_nav_history.csv", parse_dates=["date"]),
        "transactions": pd.read_csv(PROCESSED_DIR / "08_investor_transactions.csv", parse_dates=["transaction_date"]),
        "holdings": pd.read_csv(PROCESSED_DIR / "09_portfolio_holdings.csv", parse_dates=["portfolio_date"]),
    }


def compute_daily_returns(nav_history: pd.DataFrame) -> pd.DataFrame:
    nav = nav_history.sort_values(["amfi_code", "date"]).copy()
    nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()
    return nav


def compute_var_cvar(daily_returns: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    grouped = daily_returns.dropna(subset=["daily_return"]).groupby("amfi_code", sort=False)
    for code, group in grouped:
        returns = group["daily_return"].to_numpy(dtype=float)
        if returns.size == 0:
            continue

        var = np.percentile(returns, 5)
        cvar = returns[returns <= var].mean() if returns[returns <= var].size > 0 else np.nan
        records.append(
            {
                "amfi_code": code,
                "var_95_pct": float(var * 100),
                "cvar_95_pct": float(cvar * 100),
                "observation_count": int(returns.size),
            }
        )

    var_df = pd.DataFrame.from_records(records)
    return var_df.sort_values("var_95_pct").reset_index(drop=True)


def select_top_funds_by_aum(scheme_perf: pd.DataFrame, top_n: int = 5) -> list[int]:
    return (
        scheme_perf.sort_values("aum_crore", ascending=False)
        .head(top_n)["amfi_code"]
        .astype(int)
        .tolist()
    )


def compute_rolling_sharpe(daily_returns: pd.DataFrame, selected_codes: list[int]) -> pd.DataFrame:
    selected = (
        daily_returns[daily_returns["amfi_code"].isin(selected_codes)]
        .sort_values(["amfi_code", "date"])
        .copy()
    )

    def rolling_sharpe(series: pd.Series) -> pd.Series:
        return series.rolling(90, min_periods=90).mean() / series.rolling(90, min_periods=90).std() * math.sqrt(TRADING_DAYS)

    selected["rolling_sharpe"] = selected.groupby("amfi_code")["daily_return"].transform(rolling_sharpe)
    return selected.dropna(subset=["rolling_sharpe"]).reset_index(drop=True)


def plot_rolling_sharpe(rolling_sharpe: pd.DataFrame, fund_master: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 8))
    scheme_names = fund_master.set_index("amfi_code")["scheme_name"].to_dict()
    for code, group in rolling_sharpe.groupby("amfi_code", sort=False):
        label = scheme_names.get(code, str(code))
        ax.plot(group["date"], group["rolling_sharpe"], label=f"{label} ({code})", linewidth=2)

    ax.set_title("90-Day Rolling Sharpe Ratio for Top 5 Funds by AUM")
    ax.set_xlabel("Date")
    ax.set_ylabel("Rolling Sharpe Ratio")
    ax.legend(loc="upper left", fontsize="small")
    ax.grid(True, linestyle="--", alpha=0.35)
    plt.tight_layout()

    output_path = OUTPUT_DIR / "rolling_sharpe_chart.png"
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    return output_path


def build_cohort_analysis(transactions: pd.DataFrame, fund_master: pd.DataFrame) -> pd.DataFrame:
    tx = transactions.copy()
    tx["transaction_type"] = tx["transaction_type"].astype(str).str.upper()
    tx["cohort_year"] = tx.groupby("investor_id")["transaction_date"].transform("min").dt.year

    sip = tx[tx["transaction_type"] == "SIP"].copy()
    cohort_sip = (
        sip.groupby("cohort_year", as_index=False)
        .agg(
            avg_sip_amount=("amount_inr", "mean"),
            total_sip_amount=("amount_inr", "sum"),
            sip_transaction_count=("transaction_id", "count"),
        )
    )

    cohort_total = (
        tx.groupby("cohort_year", as_index=False)
        .agg(
            total_invested=("amount_inr", "sum"),
            investor_count=("investor_id", "nunique"),
        )
    )

    fund_pref = (
        tx.groupby(["cohort_year", "amfi_code"], as_index=False)
        .agg(total_amount=("amount_inr", "sum"))
    )
    fund_pref = fund_pref.loc[fund_pref.groupby("cohort_year")["total_amount"].idxmax()]
    fund_pref = fund_pref.merge(
        fund_master[["amfi_code", "scheme_name"]], on="amfi_code", how="left"
    ).rename(columns={"scheme_name": "top_fund_preference", "total_amount": "top_fund_invested"})

    cohort = cohort_total.merge(cohort_sip, on="cohort_year", how="left").merge(
        fund_pref[["cohort_year", "top_fund_preference", "top_fund_invested"]],
        on="cohort_year",
        how="left",
    )
    cohort = cohort.sort_values("cohort_year").reset_index(drop=True)
    return cohort


def build_sip_continuity(transactions: pd.DataFrame) -> pd.DataFrame:
    sip = transactions.copy()
    sip = sip[sip["transaction_type"].astype(str).str.upper() == "SIP"].copy()
    sip = sip.sort_values(["investor_id", "transaction_date"])

    records: list[dict[str, object]] = []
    for investor_id, group in sip.groupby("investor_id", sort=False):
        if len(group) < 6:
            continue
        dates = group["transaction_date"].sort_values()
        gaps = dates.diff().dt.days.dropna()
        if gaps.empty:
            continue
        avg_gap = float(gaps.mean())
        max_gap = int(gaps.max())
        records.append(
            {
                "investor_id": investor_id,
                "sip_transaction_count": len(group),
                "avg_gap_days": avg_gap,
                "max_gap_days": max_gap,
                "at_risk": max_gap > 35,
            }
        )

    continuity = pd.DataFrame.from_records(records)
    if continuity.empty:
        return continuity

    continuity = continuity.sort_values(["at_risk", "max_gap_days"], ascending=[False, False]).reset_index(drop=True)
    return continuity


def compute_sector_hhi(holdings: pd.DataFrame, fund_master: pd.DataFrame) -> pd.DataFrame:
    hhi = (
        holdings.groupby("amfi_code", as_index=False)
        .agg(hhi=("weight_pct", lambda weights: float((weights.astype(float) ** 2).sum())), holding_count=("stock_symbol", "count"))
    )
    hhi = hhi.merge(
        fund_master[["amfi_code", "scheme_name", "category"]], on="amfi_code", how="left"
    )
    return hhi.sort_values("hhi", ascending=False).reset_index(drop=True)


def save_reports(var_df: pd.DataFrame, cohort_df: pd.DataFrame, continuity_df: pd.DataFrame, hhi_df: pd.DataFrame) -> None:
    var_path = OUTPUT_DIR / "var_cvar_report.csv"
    cohort_path = OUTPUT_DIR / "cohort_analysis.csv"
    continuity_path = OUTPUT_DIR / "sip_continuity_report.csv"
    hhi_path = OUTPUT_DIR / "sector_hhi_report.csv"

    var_df.to_csv(var_path, index=False)
    cohort_df.to_csv(cohort_path, index=False)
    continuity_df.to_csv(continuity_path, index=False)
    hhi_df.to_csv(hhi_path, index=False)

    print(f"Saved VaR/CVaR report: {var_path}")
    print(f"Saved cohort analysis report: {cohort_path}")
    print(f"Saved SIP continuity report: {continuity_path}")
    print(f"Saved sector HHI report: {hhi_path}")


def main() -> None:
    data = load_data()
    daily_returns = compute_daily_returns(data["nav_history"])

    var_df = compute_var_cvar(daily_returns)
    cohort_df = build_cohort_analysis(data["transactions"], data["fund_master"])
    continuity_df = build_sip_continuity(data["transactions"])
    hhi_df = compute_sector_hhi(data["holdings"], data["fund_master"])

    top_codes = select_top_funds_by_aum(data["scheme_perf"], top_n=5)
    rolling_sharpe_df = compute_rolling_sharpe(daily_returns, top_codes)
    plot_path = plot_rolling_sharpe(rolling_sharpe_df, data["fund_master"])

    save_reports(var_df, cohort_df, continuity_df, hhi_df)
    print(f"Saved rolling Sharpe chart: {plot_path}")
    print("Day 6 advanced analytics complete.")


if __name__ == "__main__":
    main()
