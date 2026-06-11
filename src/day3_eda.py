"""
Day 3 EDA - Exploratory Data Analysis Module
=============================================
Generate comprehensive exploratory visualizations of mutual fund datasets.
Creates interactive HTML charts and static PNG images for dashboard and reports.

This module:
- Loads cleaned datasets (fund master, NAV, AUM, SIP, transactions, holdings, etc.)
- Generates NAV trend visualization (all 40 schemes with market annotations)
- Analyzes AUM growth by fund house (bar chart with year-over-year comparison)
- Visualizes monthly SIP inflows with peak annotations
- Creates category inflow heatmaps showing sector trends
- Analyzes investor demographics (age, gender, state distribution)
- Computes folio growth metrics and sector allocation patterns
- Saves all visualizations as both interactive HTML and static PNG files
"""

from typing import Any, cast

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from matplotlib.patches import Rectangle, Circle
from pathlib import Path

sns.set(style='whitegrid', font_scale=1.0)
plt.rcParams.update({'figure.dpi': 120, 'font.size': 10})

BASE_DIR = Path(__file__).resolve().parent.parent
PLOTS_DIR = BASE_DIR / 'notebooks' / 'plots'
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Load data
fund_master = pd.read_csv(BASE_DIR / 'data' / 'processed' / '01_fund_master.csv', parse_dates=['launch_date'])
nav_history = pd.read_csv(BASE_DIR / 'data' / 'processed' / '02_nav_history.csv', parse_dates=['date'])
aum_by_house = pd.read_csv(BASE_DIR / 'data' / 'processed' / '03_aum_by_fund_house.csv', parse_dates=['date'])
sip_inflows = pd.read_csv(BASE_DIR / 'data' / 'processed' / '04_monthly_sip_inflows.csv', parse_dates=['month'])
category_inflows = pd.read_csv(BASE_DIR / 'data' / 'processed' / '05_category_inflows.csv', parse_dates=['month'])
folio_count = pd.read_csv(BASE_DIR / 'data' / 'processed' / '06_industry_folio_count.csv', parse_dates=['month'])
scheme_perf = pd.read_csv(BASE_DIR / 'data' / 'processed' / '07_scheme_performance.csv')
transactions = pd.read_csv(BASE_DIR / 'data' / 'processed' / '08_investor_transactions.csv', parse_dates=['transaction_date'])
portfolio_holdings = pd.read_csv(BASE_DIR / 'data' / 'processed' / '09_portfolio_holdings.csv', parse_dates=['portfolio_date'])
benchmark = pd.read_csv(BASE_DIR / 'data' / 'processed' / '10_benchmark_indices.csv', parse_dates=['date'])

NAV_PNG = PLOTS_DIR / 'nav_trends.png'
AUM_PNG = PLOTS_DIR / 'aum_growth_by_house.png'
SIP_PNG = PLOTS_DIR / 'sip_trend_monthly.png'
CAT_HEATMAP_PNG = PLOTS_DIR / 'category_inflow_heatmap.png'
AGE_PIE_PNG = PLOTS_DIR / 'investor_age_distribution.png'
SIP_AGE_BOX_PNG = PLOTS_DIR / 'sip_amount_by_age_group.png'
GENDER_SPLIT_PNG = PLOTS_DIR / 'gender_split_sip.png'
STATE_SIP_PNG = PLOTS_DIR / 'sip_amount_by_state.png'
CITY_TIER_PNG = PLOTS_DIR / 'city_tier_pie.png'
FOLIO_GROWTH_PNG = PLOTS_DIR / 'folio_count_growth.png'
FOLIO_COMPOSITION_PNG = PLOTS_DIR / 'folio_composition_by_category.png'
CORR_MATRIX_PNG = PLOTS_DIR / 'nav_return_correlation_matrix.png'
SECTOR_DONUT_PNG = PLOTS_DIR / 'sector_allocation_donut.png'

# 1. NAV trend for all 40 schemes
fig = px.line(
    nav_history.sort_values(['amfi_code', 'date']),
    x='date', y='nav', color='amfi_code',
    title='Daily NAV Trend for 40 Mutual Fund Schemes (2022-2026)',
    labels={'nav': 'NAV', 'date': 'Date', 'amfi_code': 'AMFI Code'}
)
fig.update_layout(showlegend=False)
# use subtle RGBA fills and place shapes beneath traces to avoid visible overlay lines
fig.add_vrect(x0='2023-01-01', x1='2023-12-31', fillcolor='rgba(0,200,0,0.06)', line_width=0, layer='below', annotation_text='2023 bull run', annotation_position='top left')
fig.add_vrect(x0='2024-01-01', x1='2024-12-31', fillcolor='rgba(200,0,0,0.06)', line_width=0, layer='below', annotation_text='2024 correction phase', annotation_position='top right')
fig.write_html(PLOTS_DIR / 'nav_trends.html')
fig.write_image(NAV_PNG)

# 2. AUM growth grouped bar chart by fund house per year
fund_house_year = (
    aum_by_house.assign(year=aum_by_house['date'].dt.year)
    .query('year >= 2022 and year <= 2025')
    .groupby(['fund_house', 'year'], as_index=False)
    .agg(aum_crore=('aum_crore', 'sum'))
)
plt.figure(figsize=(14, 7))
ax = sns.barplot(data=fund_house_year, x='fund_house', y='aum_crore', hue='year', palette='viridis')
ax.set_title('AUM Growth by Fund House (2022-2025)')
ax.set_xlabel('Fund House')
ax.set_ylabel('AUM (Crore INR)')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
for p in ax.patches:
    if not isinstance(p, Rectangle):
        continue
    height = p.get_height()
    if height > 0:
        ax.annotate(
            f'{int(height):,}',
            (p.get_x() + p.get_width() / 2, height),
            ha='center',
            va='bottom',
            fontsize=7,
            rotation=90,
        )
plt.tight_layout()
plt.savefig(AUM_PNG)
plt.close()

# 3. SIP inflow trend with annotation for all-time high
sip_sort = sip_inflows.query('month >= "2022-01-01" and month <= "2025-12-31"').sort_values('month')
fig = px.line(sip_sort, x='month', y='sip_inflow_crore', title='Monthly SIP Inflows (Jan 2022 - Dec 2025)', markers=True)
max_row = sip_sort.loc[sip_sort['sip_inflow_crore'].idxmax()]
max_month = cast(str, pd.Timestamp(cast(Any, max_row['month'])).isoformat())
max_value = cast(float, float(cast(Any, max_row['sip_inflow_crore'])))
fig.add_annotation(
    x=max_month,
    y=max_value,
    text=f"₹{int(max_value):,} Cr peak (Dec 2025)",
    showarrow=True,
    arrowhead=2,
)
fig.update_layout(xaxis_title='Month', yaxis_title='SIP Inflow (Crore INR)')
fig.write_html(PLOTS_DIR / 'sip_trend.html')
fig.write_image(SIP_PNG)

# 4. Category inflow heatmap
cat_pivot = category_inflows.pivot_table(index='category', columns='month', values='net_inflow_crore', aggfunc='sum').fillna(0)
plt.figure(figsize=(14, 8))
sns.heatmap(cat_pivot, annot=True, fmt='.0f', cmap='YlGnBu', linewidths=0.5)
plt.title('Category Inflow Heatmap (Net Inflow Crore)')
plt.xlabel('Month')
plt.ylabel('Fund Category')
plt.tight_layout()
plt.savefig(CAT_HEATMAP_PNG)
plt.close()

# 5. Investor demographics: age group pie and SIP amount box plot
sip_tx = transactions.query("transaction_type == 'SIP'")
age_counts = sip_tx['age_group'].value_counts()
age_labels = age_counts.index.astype(str).tolist()
plt.figure(figsize=(7, 7))
plt.pie(age_counts, labels=age_labels, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'white'})
plt.title('Investor Age Group Distribution for SIP Transactions')
plt.tight_layout()
plt.savefig(AGE_PIE_PNG)
plt.close()

plt.figure(figsize=(12, 6))
sns.boxplot(data=sip_tx, x='age_group', y='amount_inr', palette='pastel')
plt.title('SIP Amount Distribution by Investor Age Group')
plt.xlabel('Age Group')
plt.ylabel('SIP Amount (INR)')
plt.tight_layout()
plt.savefig(SIP_AGE_BOX_PNG)
plt.close()

# Gender split of SIP transactions
gender_counts = sip_tx['gender'].value_counts()
gender_labels = gender_counts.index.astype(str).tolist()
plt.figure(figsize=(7, 7))
plt.pie(gender_counts, labels=gender_labels, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'white'})
plt.title('Gender Split of SIP Transactions')
plt.tight_layout()
plt.savefig(GENDER_SPLIT_PNG)
plt.close()

# 6. Geographic distribution: SIP amount by state
state_sip = (
    sip_tx.groupby('state', as_index=False)
    .agg(amount_inr=('amount_inr', 'sum'))
    .sort_values(by='amount_inr', ascending=False)
)
plt.figure(figsize=(12, 8))
sns.barplot(data=state_sip.head(15), y='state', x='amount_inr', palette='coolwarm')
plt.title('Top SIP Amount by State')
plt.xlabel('Total SIP Amount (INR)')
plt.ylabel('State')
plt.tight_layout()
plt.savefig(STATE_SIP_PNG)
plt.close()

# T30 vs B30 city tier share for SIP
city_tier = sip_tx['city_tier'].value_counts()
city_tier_labels = city_tier.index.astype(str).tolist()
plt.figure(figsize=(6, 6))
plt.pie(city_tier, labels=city_tier_labels, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'white'})
plt.title('SIP Share by City Tier (T30 vs B30)')
plt.tight_layout()
plt.savefig(CITY_TIER_PNG)
plt.close()

# 7. Folio count growth line chart and milestone markers
plt.figure(figsize=(14, 7))
sns.lineplot(data=folio_count.sort_values('month'), x='month', y='total_folios_crore', marker='o')
plt.title('Folio Count Growth (Jan 2022 to Dec 2025)')
plt.xlabel('Month')
plt.ylabel('Total Folios (Crore)')
for date_str, value in [('2022-01-01', 13.26), ('2023-01-01', 14.81), ('2024-01-01', 18.02), ('2025-12-01', 26.12)]:
    date_value = cast(Any, pd.to_datetime(date_str).to_pydatetime())
    plt.scatter(date_value, value, s=80, color='red')
    plt.text(date_value, value + 0.8, f'{value} Cr', ha='center', color='red')
plt.tight_layout()
plt.savefig(FOLIO_GROWTH_PNG)
plt.close()

# Folio composition by equity/debt/hybrid
plt.figure(figsize=(14, 7))
folio_long = folio_count.melt(id_vars=['month'], value_vars=['equity_folios_crore', 'debt_folios_crore', 'hybrid_folios_crore'], var_name='folio_type', value_name='crore')
folio_long['folio_type'] = folio_long['folio_type'].str.replace('_folios_crore', '').str.title()
sns.lineplot(data=folio_long, x='month', y='crore', hue='folio_type', marker='o')
plt.title('Folio Segment Growth by Asset Class')
plt.xlabel('Month')
plt.ylabel('Folios (Crore)')
plt.legend(title='Folio Type')
plt.tight_layout()
plt.savefig(FOLIO_COMPOSITION_PNG)
plt.close()

# 8. NAV daily returns correlation matrix for 10 selected funds
merge_master = nav_history.merge(fund_master[['amfi_code', 'scheme_name']], on='amfi_code', how='left')
selected_amfi = scheme_perf.sort_values('aum_crore', ascending=False).head(10)['amfi_code'].tolist()
returns = (
    nav_history[nav_history['amfi_code'].isin(selected_amfi)]
    .sort_values(['amfi_code', 'date'])
    .groupby('amfi_code')
    .apply(lambda x: x.assign(daily_return=x['nav'].pct_change()))
    .reset_index(drop=True)
)
returns_pivot = returns.pivot(index='date', columns='amfi_code', values='daily_return').dropna()
corr_matrix = returns_pivot.corr()
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, linewidths=0.5)
plt.title('Pairwise Correlation of Daily NAV Returns for 10 Selected Funds')
plt.tight_layout()
plt.savefig(CORR_MATRIX_PNG)
plt.close()

# 9. Sector allocation donut chart
sector_alloc = (
    portfolio_holdings.groupby('sector', as_index=False)
    .agg(weight_pct=('weight_pct', 'sum'))
    .sort_values(by='weight_pct', ascending=False)
)
plt.figure(figsize=(8, 8))
sector_labels = sector_alloc['sector'].astype(str).tolist()
plt.pie(sector_alloc['weight_pct'], labels=sector_labels, autopct='%1.1f%%', startangle=140, pctdistance=0.82)
centre_circle = Circle((0, 0), 0.55, fc='white')
plt.gca().add_artist(centre_circle)
plt.title('Aggregate Sector Allocation Across Equity Portfolios')
plt.tight_layout()
plt.savefig(SECTOR_DONUT_PNG)
plt.close()

print('Saved PNG charts to', PLOTS_DIR)
