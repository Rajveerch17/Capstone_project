# Day 6 Advanced Analytics Summary

## Overview
- Completed Day 6 advanced analytics deliverables using cleaned mutual fund data and investor transaction information.
- Built `src/day6_advanced_analytics.py` to compute portfolio risk metrics, investor cohort behavior, SIP continuity signals, and sector concentration measures.
- Added a simple recommender script at `src/recommender.py` to suggest top funds based on risk appetite (Low / Moderate / High).
- Executed the analysis notebook `notebooks/Advanced_Analytics.ipynb` and produced an executed notebook version `notebooks/Advanced_Analytics_executed.ipynb` with output graphs.

## Key findings
- Historical VaR and CVaR were computed for all 40 schemes, identifying funds with the largest downside exposure during market stress.
- Rolling 90-day Sharpe ratios were plotted for the top 5 funds by AUM, showing how risk-adjusted performance evolved over time.
- Investor cohort analysis grouped investors by first transaction year and computed average SIP amount, total invested amount, and top fund preference per cohort.
- SIP continuity analysis flagged investors with 6+ SIP transactions and maximum gaps over 35 days, highlighting potential at-risk SIP behavior.
- Sector concentration was measured using the Herfindahl-Hirschman Index (HHI) for each equity fund, identifying funds with the most concentrated holdings.

## Deliverables generated
- `src/day6_advanced_analytics.py`
- `src/recommender.py`
- `notebooks/Advanced_Analytics.ipynb`
- `notebooks/Advanced_Analytics_executed.ipynb`
- `var_cvar_report.csv`
- `cohort_analysis.csv`
- `sip_continuity_report.csv`
- `sector_hhi_report.csv`
- `rolling_sharpe_chart.png`

## Notes
- The notebook was executed successfully with no runtime errors.
- The recommender script uses Sharpe ratio within the chosen risk grade to recommend the top 3 funds.
- Day 6 outputs are saved in the project root for easy review and integration with reports.
