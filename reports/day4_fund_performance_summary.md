# Day 4 Fund Performance Analytics Summary

## Overview
- Completed Day 4 fund performance analytics for the 40 mutual fund schemes using processed NAV and benchmark data.
- Computed daily NAV returns, horizon CAGR, risk-adjusted metrics, regression-based alpha/beta, maximum drawdown, and a composite fund scorecard.
- Produced script and notebook deliverables along with CSV outputs and a benchmark comparison chart.

## Key findings
- Daily return distributions were validated and show a mean close to zero with moderate volatility, confirming clean NAV series behavior.
- Multi-year horizon analysis produced 1-year, 3-year, and 5-year CAGR estimates for each fund, enabling consistent performance comparison.
- Sharpe ratio and Sortino ratio were computed using a 6.5% risk-free rate proxy, facilitating risk-adjusted fund ranking.
- Alpha and beta were estimated by regressing fund returns against NIFTY100 daily returns, capturing relative market exposure and excess return potential.
- Maximum drawdown analysis identified each fund's worst peak-to-trough NAV decline and the corresponding drawdown period.
- A composite fund scorecard was built using: 30% 3-year return rank, 25% Sharpe rank, 20% alpha rank, 15% expense ratio rank (inverse), and 10% max drawdown rank (inverse).
- Top funds were compared against NIFTY50 and NIFTY100 over the latest 3-year period in a benchmark comparison chart.

## Deliverables generated
- `src/day4_fund_performance.py`
- `notebooks/Performance_Analytics.ipynb`
- `fund_scorecard.csv`
- `alpha_beta.csv`
- `performance_comparison.csv`
- `notebooks/plots/benchmark_comparison_chart.png`

## Notes
- The Day 4 analytics use cleaned inputs from `data/processed/`.
- Output CSVs are saved in the project root for easy review and downstream reporting.
- The benchmark comparison chart visualizes the indexed performance of the top 5 ranked funds versus NIFTY50 and NIFTY100.
