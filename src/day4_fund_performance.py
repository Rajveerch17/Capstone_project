from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import linregress

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR
PLOTS_DIR = BASE_DIR / "notebooks" / "plots"

PLOTS_DIR.mkdir(parents=True, exist_ok=True)

RF_RATE = 0.065
TRADING_DAYS = 252


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    nav_history = pd.read_csv(PROCESSED_DIR / "02_nav_history.csv", parse_dates=["date"])
    benchmark = pd.read_csv(PROCESSED_DIR / "10_benchmark_indices.csv", parse_dates=["date"])
    fund_master = pd.read_csv(PROCESSED_DIR / "01_fund_master.csv")
    scheme_perf = pd.read_csv(PROCESSED_DIR / "07_scheme_performance.csv")
    return nav_history, benchmark, fund_master, scheme_perf


def compute_daily_returns(nav_history: pd.DataFrame) -> pd.DataFrame:
    nav = nav_history.sort_values(["amfi_code", "date"]).copy()
    nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()
    return nav


def compute_horizon_cagr(nav: pd.DataFrame, horizon_years: int) -> pd.Series:
    result = []
    for code, group in nav.groupby("amfi_code", sort=False):
        group = group.sort_values("date").reset_index(drop=True)
        end_date = group["date"].max()
        target_date = end_date - pd.DateOffset(years=horizon_years)
        earliest = group[group["date"] <= target_date]
        if earliest.empty:
            result.append((code, np.nan))
            continue
        start_nav = earliest.iloc[-1]["nav"]
        end_nav = group.iloc[-1]["nav"]
        cagr = (end_nav / start_nav) ** (1 / horizon_years) - 1
        result.append((code, cagr))
    return pd.Series({code: cagr for code, cagr in result})


def annualized_statistics(returns: pd.Series) -> tuple[float, float]:
    mean_daily = returns.mean()
    std_daily = returns.std(ddof=0)
    annualized_return = mean_daily * TRADING_DAYS
    annualized_vol = std_daily * np.sqrt(TRADING_DAYS)
    return annualized_return, annualized_vol


def compute_sharpe_sortino(returns: pd.Series) -> tuple[float, float]:
    annualized_return, annualized_vol = annualized_statistics(returns)
    sharpe = np.nan
    sortino = np.nan
    if annualized_vol > 0:
        sharpe = (annualized_return - RF_RATE) / annualized_vol
    downside = returns[returns < 0]
    downside_std = downside.std(ddof=0)
    if downside_std > 0:
        sortino = (annualized_return - RF_RATE) / (downside_std * np.sqrt(TRADING_DAYS))
    return sharpe, sortino


def compute_alpha_beta(fund_returns: pd.Series, benchmark_returns: pd.Series) -> tuple[float, float, float]:
    merged = pd.DataFrame({"fund": fund_returns, "benchmark": benchmark_returns}).dropna()
    if merged.empty:
        return np.nan, np.nan, np.nan
    regression: Any = linregress(merged["benchmark"], merged["fund"])
    slope = float(regression.slope)
    intercept = float(regression.intercept)
    r_value = float(regression.rvalue)
    alpha_annual = intercept * TRADING_DAYS
    return slope, alpha_annual, r_value ** 2


def compute_drawdown(nav_group: pd.DataFrame) -> tuple[float, pd.Timestamp | None, pd.Timestamp | None]:
    running_max = nav_group["nav"].cummax()
    drawdowns = nav_group["nav"] / running_max - 1
    trough_idx = drawdowns.idxmin()
    trough_value = float(running_max.loc[trough_idx])
    trough_date = pd.to_datetime(nav_group.loc[trough_idx, "date"])  # type: ignore[arg-type]
    peak_candidates = nav_group.loc[:trough_idx]
    peak_date_series = peak_candidates.loc[peak_candidates["nav"] == trough_value, "date"]
    peak_date = pd.to_datetime(peak_date_series.max()) if not peak_date_series.empty else None  # type: ignore[arg-type]
    return float(drawdowns.loc[trough_idx]), peak_date, trough_date


def build_performance_frame(nav: pd.DataFrame, benchmark: pd.DataFrame, fund_master: pd.DataFrame) -> pd.DataFrame:
    benchmark_wide = (
        benchmark.pivot(index="date", columns="index_name", values="close_value")
        .sort_index()
    )
    benchmark_wide = benchmark_wide.assign(
        NIFTY50_return=benchmark_wide["NIFTY50"].pct_change(),
        NIFTY100_return=benchmark_wide["NIFTY100"].pct_change(),
    )

    nav_with_returns = nav.dropna(subset=["daily_return"]).copy()
    records = []

    for code, group in nav_with_returns.groupby("amfi_code", sort=False):
        group = group.sort_values("date").reset_index(drop=True)
        if group.empty:
            continue

        latest = group["date"].max()
        one_year_cagr = compute_horizon_cagr(group, 1).get(code, np.nan)
        three_year_cagr = compute_horizon_cagr(group, 3).get(code, np.nan)
        five_year_cagr = compute_horizon_cagr(group, 5).get(code, np.nan)

        sharpe, sortino = compute_sharpe_sortino(group["daily_return"])
        drawdown, peak_date, trough_date = compute_drawdown(group)

        benchmark_frame = benchmark_wide.reset_index()[["date", "NIFTY100_return"]]
        joined = pd.merge(group[["date", "daily_return"]], benchmark_frame, on="date", how="inner")
        beta, alpha, r2 = compute_alpha_beta(joined["daily_return"], joined["NIFTY100_return"])
        tracking_error = np.nan
        if not joined.empty:
            diff = (joined["daily_return"] - joined["NIFTY100_return"]).to_numpy(dtype=float)
            tracking_error = float(np.nanstd(diff, ddof=0) * np.sqrt(TRADING_DAYS))

        records.append(
            {
                "amfi_code": code,
                "scheme_name": fund_master.loc[fund_master["amfi_code"] == code, "scheme_name"].iloc[0]
                if code in fund_master["amfi_code"].values
                else np.nan,
                "3yr_cagr_pct": three_year_cagr * 100 if pd.notna(three_year_cagr) else np.nan,
                "1yr_cagr_pct": one_year_cagr * 100 if pd.notna(one_year_cagr) else np.nan,
                "5yr_cagr_pct": five_year_cagr * 100 if pd.notna(five_year_cagr) else np.nan,
                "annualized_return_pct": annualized_statistics(group["daily_return"])[0] * 100,
                "annualized_vol_pct": annualized_statistics(group["daily_return"])[1] * 100,
                "sharpe_ratio": sharpe,
                "sortino_ratio": sortino,
                "alpha_pct": alpha * 100,
                "beta": beta,
                "r_squared": r2,
                "tracking_error_pct": tracking_error * 100,
                "max_drawdown_pct": drawdown * 100,
                "drawdown_start": peak_date,
                "drawdown_end": trough_date,
            }
        )

    return pd.DataFrame.from_records(records)


def build_scorecard(perf: pd.DataFrame, scheme_perf: pd.DataFrame) -> pd.DataFrame:
    merged = perf.merge(scheme_perf[["amfi_code", "expense_ratio_pct"]], on="amfi_code", how="left")
    merged = merged.sort_values("amfi_code").reset_index(drop=True)

    n = len(merged)
    merged["rank_3yr"] = merged["3yr_cagr_pct"].rank(ascending=False, method="min")
    merged["rank_sharpe"] = merged["sharpe_ratio"].rank(ascending=False, method="min")
    merged["rank_alpha"] = merged["alpha_pct"].rank(ascending=False, method="min")
    merged["rank_expense"] = merged["expense_ratio_pct"].rank(ascending=True, method="min")
    merged["rank_max_dd"] = merged["max_drawdown_pct"].rank(ascending=True, method="min")

    for col in ["rank_3yr", "rank_sharpe", "rank_alpha", "rank_expense", "rank_max_dd"]:
        merged[f"rank_pct_{col}"] = 100 * (1 - (merged[col] - 1) / max(n - 1, 1))

    merged["fund_score"] = (
        merged["rank_pct_rank_3yr"] * 0.30
        + merged["rank_pct_rank_sharpe"] * 0.25
        + merged["rank_pct_rank_alpha"] * 0.20
        + merged["rank_pct_rank_expense"] * 0.15
        + merged["rank_pct_rank_max_dd"] * 0.10
    )
    merged["fund_score"] = merged["fund_score"].round(2)

    score_cols = [
        "amfi_code",
        "scheme_name",
        "fund_score",
        "3yr_cagr_pct",
        "sharpe_ratio",
        "alpha_pct",
        "expense_ratio_pct",
        "max_drawdown_pct",
        "rank_3yr",
        "rank_sharpe",
        "rank_alpha",
        "rank_expense",
        "rank_max_dd",
    ]
    return merged[score_cols].sort_values("fund_score", ascending=False).reset_index(drop=True)


def build_alpha_beta_table(perf: pd.DataFrame) -> pd.DataFrame:
    return perf[["amfi_code", "scheme_name", "alpha_pct", "beta", "r_squared", "tracking_error_pct"]].sort_values("alpha_pct", ascending=False).reset_index(drop=True)


def save_outputs(perf: pd.DataFrame, scorecard: pd.DataFrame, alpha_beta: pd.DataFrame) -> None:
    perf_path = OUTPUT_DIR / "performance_comparison.csv"
    scorecard_path = OUTPUT_DIR / "fund_scorecard.csv"
    alpha_beta_path = OUTPUT_DIR / "alpha_beta.csv"

    perf.to_csv(perf_path, index=False)
    scorecard.to_csv(scorecard_path, index=False)
    alpha_beta.to_csv(alpha_beta_path, index=False)

    print(f"Saved performance comparison table to {perf_path}")
    print(f"Saved fund scorecard to {scorecard_path}")
    print(f"Saved alpha/beta table to {alpha_beta_path}")


def plot_top5_benchmarks(nav: pd.DataFrame, benchmark: pd.DataFrame, scorecard: pd.DataFrame) -> None:
    latest_date = nav["date"].max()
    start_date = latest_date - pd.DateOffset(years=3)
    top5_codes = scorecard.head(5)["amfi_code"].tolist()

    plot_nav = nav[nav["amfi_code"].isin(top5_codes) & (nav["date"] >= start_date)].copy()
    plot_nav["index_value"] = plot_nav.groupby("amfi_code")["nav"].transform(lambda x: x / x.iloc[0] * 100)
    benchmark_plot = benchmark[benchmark["index_name"].isin(["NIFTY50", "NIFTY100"]) & (benchmark["date"] >= start_date)].copy()
    benchmark_plot["index_value"] = benchmark_plot.groupby("index_name")["close_value"].transform(lambda x: x / x.iloc[0] * 100)

    plt.figure(figsize=(14, 8))
    sns.set_style("whitegrid")
    scheme_name_map = scorecard.set_index("amfi_code")["scheme_name"].to_dict()
    for code in top5_codes:
        scheme_name = scheme_name_map.get(code, "")
        sub = plot_nav[plot_nav["amfi_code"] == code]
        plt.plot(sub["date"], sub["index_value"], label=f"{scheme_name} ({code})")

    for idx_name in ["NIFTY50", "NIFTY100"]:
        sub = benchmark_plot[benchmark_plot["index_name"] == idx_name]
        plt.plot(sub["date"], sub["index_value"], label=idx_name, linestyle="--", linewidth=2)

    plt.title("Top 5 Funds vs NIFTY50 and NIFTY100: 3-Year Indexed Performance")
    plt.xlabel("Date")
    plt.ylabel("Indexed Performance (Base = 100)")
    plt.legend(loc="upper left", fontsize="small")
    plt.tight_layout()
    output_path = PLOTS_DIR / "benchmark_comparison_chart.png"
    plt.savefig(output_path)
    plt.close()
    print(f"Saved benchmark comparison chart to {output_path}")


def main() -> None:
    nav_history, benchmark, fund_master, scheme_perf = load_data()
    daily_returns = compute_daily_returns(nav_history)
    perf = build_performance_frame(daily_returns, benchmark, fund_master)
    scorecard = build_scorecard(perf, scheme_perf)
    alpha_beta = build_alpha_beta_table(perf)
    save_outputs(perf, scorecard, alpha_beta)
    plot_top5_benchmarks(daily_returns, benchmark, scorecard)

    validation = daily_returns["daily_return"].dropna().describe()
    print("\nDaily return distribution summary:")
    print(validation)


if __name__ == "__main__":
    main()
