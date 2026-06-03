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
