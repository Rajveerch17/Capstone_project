# Day 3 EDA Summary

## Overview
- Completed Day 3 exploratory data analysis using processed mutual fund datasets and investor transaction data.
- Generated visual analytics for NAV trends, AUM growth, SIP behavior, investor demographics, geographic SIP distributions, folio growth, return correlations, and sector allocation.
- Produced both Python script and notebook deliverables for Day 3.

## Key findings
- NAV trend analysis covered 40 mutual fund schemes and highlighted a strong bull run in 2023 followed by a correction phase in 2024.
- AUM growth by fund house showed sustained expansion from 2022 through 2025, with larger houses consistently capturing higher market share.
- Monthly SIP inflows exhibited a rising trajectory, reaching an all-time high peak late in the dataset period.
- Category-level inflows were visualized in a heatmap, revealing months with the strongest net inflows by fund category.
- Investor demographics indicated a broad age-group mix for SIP investors, with clear differences in SIP amount distributions across age groups.
- Gender split analysis confirmed the relative share of SIP activity between male and female investors.
- Geographic SIP concentration was strongest in the top states, while city-tier analysis showed the distribution between T30 and B30 cities.
- Folio count growth demonstrated steady expansion in total folios from 2022 through 2025, with clear portfolio composition differences across equity, debt, and hybrid folios.
- Daily NAV return correlations among the top 10 funds revealed relative co-movement patterns and diversification opportunities.
- Sector allocation across portfolio holdings was summarized in a donut chart, showing the major sector weight concentrations.

## Deliverables generated
- `src/day3_eda.py` - Day 3 EDA script to generate charts and export PNG/HTML visuals.
- `notebooks/EDA_Analysis.ipynb` - Analytical notebook for Day 3 findings.
- `notebooks/EDA_Analysis_executed.ipynb` - Executed notebook output.
- `notebooks/plots/` - exported plot images and supporting HTML.

## Notes
- The Day 3 script uses processed inputs from `data/processed/`.
- Plots include NAV trend overlays, monthly SIP trend annotation, category heatmap, demographic pies/boxplots, geographic SIP bars, folio segment growth, return correlation heatmap, and sector allocation donut.
