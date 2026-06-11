"""
Fund Recommender System Module
==============================
Simple rule-based fund recommendation engine based on investor risk appetite.
Suggests top-3 funds for Low, Moderate, or High risk profiles using Sharpe ratio.

This module:
- Loads scheme performance data with risk grades and Sharpe ratios
- Maps risk appetite (Low/Moderate/High) to SEBI risk categories
- Filters eligible funds for the selected risk appetite
- Ranks by Sharpe ratio (risk-adjusted return) to select top 3 recommendations
- Displays key metrics (AMFI code, scheme name, Sharpe ratio, max drawdown, AUM)
- Provides a command-line interface for interactive recommendations

Usage:
    python recommender.py Low      # Recommend low-risk funds
    python recommender.py Moderate # Recommend moderate-risk funds
    python recommender.py High     # Recommend high-risk funds
"""

from __future__ import annotations

from pathlib import Path
import argparse
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RISK_MAP = {
    "LOW": ["Low"],
    "MODERATE": ["Moderate"],
    "HIGH": ["High", "Moderately High", "Very High"],
}


def load_scheme_performance() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "07_scheme_performance.csv")


def recommend_funds(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    appetite_key = risk_appetite.strip().upper()
    if appetite_key not in RISK_MAP:
        raise ValueError("Risk appetite must be one of: Low, Moderate, High")

    scheme_perf = load_scheme_performance()
    valid_risks = RISK_MAP[appetite_key]
    eligible = scheme_perf[scheme_perf["risk_grade"].isin(valid_risks)].copy()
    if eligible.empty:
        raise ValueError(f"No funds available for risk appetite: {risk_appetite}")

    recommended = eligible.sort_values("sharpe_ratio", ascending=False).head(top_n)
    return recommended[
        ["amfi_code", "scheme_name", "fund_house", "risk_grade", "sharpe_ratio", "max_drawdown_pct", "aum_crore"]
    ].reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fund recommender for Low / Moderate / High risk appetite")
    parser.add_argument(
        "risk_appetite",
        type=str,
        choices=["Low", "Moderate", "High"],
        help="Risk appetite: Low, Moderate, or High",
    )
    args = parser.parse_args()

    recommendations = recommend_funds(args.risk_appetite)
    print(f"Top {len(recommendations)} recommended funds for {args.risk_appetite} risk appetite:\n")
    print(recommendations.to_string(index=False, formatters={"sharpe_ratio": "{:.2f}".format, "max_drawdown_pct": "{:.2f}".format, "aum_crore": "{:.0f}".format}))


if __name__ == "__main__":
    main()
