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
