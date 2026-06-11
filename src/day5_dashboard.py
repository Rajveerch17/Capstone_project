"""
Day 5 Interactive Dashboard Module
==================================
Build multi-page interactive dashboard visualizations of mutual fund analytics.
Generate publication-ready HTML dashboards with KPIs, performance charts, and heatmaps.

This module:
- Loads cleaned mutual fund and transaction datasets
- Applies Bluestock brand color scheme and styling
- Builds KPI indicators (total AUM, SIP inflows, active folios, scheme count)
- Creates Page 1: Industry overview with AUM trends and AMC rankings
- Creates Page 2: Fund performance with risk-return scatter plots and top-15 scorecard
- Creates Page 3: Investor demographics with SIP trends by state, age, gender
- Creates Page 4: Category and sector analysis with inflow trends and allocation heatmaps
- Combines all pages into a single multi-tab dashboard HTML file
- Exports both HTML and static PNG images of all visualizations
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "dashboard"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DASHBOARD_HTML = OUTPUT_DIR / "bluestock_dashboard.html"
DASHBOARD_PDF = OUTPUT_DIR / "bluestock_dashboard.pdf"

BLUESTOCK_COLORS = ["#0e4d92", "#00a1de", "#f2a900", "#1e5b3a", "#c72c48", "#8f5a9b"]


def load_cleaned_data() -> dict[str, pd.DataFrame]:
    return {
        "fund_master": pd.read_csv(PROCESSED_DIR / "01_fund_master.csv"),
        "nav_history": pd.read_csv(PROCESSED_DIR / "02_nav_history.csv", parse_dates=["date"]),
        "aum_by_house": pd.read_csv(PROCESSED_DIR / "03_aum_by_fund_house.csv", parse_dates=["date"]),
        "sip_inflows": pd.read_csv(PROCESSED_DIR / "04_monthly_sip_inflows.csv"),
        "category_inflows": pd.read_csv(PROCESSED_DIR / "05_category_inflows.csv"),
        "scheme_perf": pd.read_csv(PROCESSED_DIR / "07_scheme_performance.csv"),
        "transactions": pd.read_csv(PROCESSED_DIR / "08_investor_transactions.csv", parse_dates=["transaction_date"]),
        "benchmark": pd.read_csv(PROCESSED_DIR / "10_benchmark_indices.csv", parse_dates=["date"]),
        "fund_scorecard": pd.read_csv(BASE_DIR / "fund_scorecard.csv"),
    }


def bluestock_layout(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Arial", color="#0d1b33"),
        colorway=BLUESTOCK_COLORS,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        title_font=dict(size=20, family="Arial", color="#0d1b33"),
        legend=dict(bgcolor="#f8f9fb", bordercolor="#e5e8eb", borderwidth=1),
        margin=dict(l=40, r=40, t=80, b=40),
    )
    return fig


def build_kpis(data: dict[str, pd.DataFrame]) -> dict[str, float]:
    aum = data["aum_by_house"].copy()
    latest_date = aum["date"].max()
    latest_aum = aum.loc[aum["date"] == latest_date, "aum_crore"].sum() # type: ignore
    sip = data["sip_inflows"].copy()
    latest_sip = sip["sip_inflow_crore"].sum()
    latest_folios = float(sip.loc[sip["month"] == sip["month"].max(), "active_sip_accounts_crore"].iloc[0]) # type: ignore
    scheme_count = data["fund_master"]["amfi_code"].nunique()
    return {
        "Total AUM (Cr)": float(latest_aum),
        "Total SIP Inflows (Cr)": float(latest_sip),
        "Active SIP Folios (Cr)": latest_folios,
        "Schemes": float(scheme_count),
        "AUM Date": latest_date,
        "SIP Latest Month": sip["month"].max(),
    }


def page1_overview(data: dict[str, pd.DataFrame]) -> list[Path]:
    kpis = build_kpis(data)
    aum_by_house = data["aum_by_house"].copy()
    aum_by_house["date"] = pd.to_datetime(aum_by_house["date"])
    total_aum_by_date = (
        aum_by_house.groupby("date", as_index=False)["aum_crore"].sum().sort_values("date")
    ) # type: ignore
    latest_aum_house = (
        aum_by_house[aum_by_house["date"] == aum_by_house["date"].max()]
        .sort_values("aum_crore", ascending=False)
    )

    # KPI indicators
    fig_kpis = make_subplots(rows=1, cols=4, specs=[[{"type": "indicator"}] * 4])
    fig_kpis.add_trace(go.Indicator(
        mode="number+delta", title={"text": "Total AUM (Cr)"}, value=kpis["Total AUM (Cr)"],
        number={'valueformat': ',.0f'}, domain={'x': [0, 1], 'y': [0, 1]}), row=1, col=1)
    fig_kpis.add_trace(go.Indicator(
        mode="number+delta", title={"text": "Total SIP Inflows (Cr)"}, value=kpis["Total SIP Inflows (Cr)"],
        number={'valueformat': ',.0f'}), row=1, col=2)
    fig_kpis.add_trace(go.Indicator(
        mode="number+delta", title={"text": "Active SIP Folios (Cr)"}, value=kpis["Active SIP Folios (Cr)"],
        number={'valueformat': '.2f'}), row=1, col=3)
    fig_kpis.add_trace(go.Indicator(
        mode="number", title={"text": "Schemes"}, value=kpis["Schemes"],
        number={'valueformat': ',.0f'}), row=1, col=4)
    fig_kpis.update_layout(height=240, title_text="Industry Overview KPI Summary")
    bluestock_layout(fig_kpis)
    page1_kpi = OUTPUT_DIR / "page1_kpis.png"
    fig_kpis.write_image(str(page1_kpi), width=1600, height=300)
    fig_kpis.write_html(str(OUTPUT_DIR / "page1_kpis.html"), include_plotlyjs="cdn")

    fig_aum_trend = px.line(
        total_aum_by_date,
        x="date",
        y="aum_crore",
        title="Industry AUM Trend (2022–2025)",
        markers=True,
    )
    fig_aum_trend.update_layout(yaxis_title="AUM (Cr)")
    bluestock_layout(fig_aum_trend)
    page1_trend = OUTPUT_DIR / "page1_aum_trend.png"
    fig_aum_trend.write_image(str(page1_trend), width=1400, height=700)
    fig_aum_trend.write_html(str(OUTPUT_DIR / "page1_aum_trend.html"), include_plotlyjs="cdn")

    fig_aum_bar = px.bar(
        latest_aum_house,
        x="fund_house",
        y="aum_crore",
        title="AUM by AMC (Latest Period)",
        color="fund_house",
        text="aum_crore",
        labels={"aum_crore": "AUM (Cr)", "fund_house": "Fund House"},
    )
    fig_aum_bar.update_layout(showlegend=False, xaxis_tickangle=-45)
    fig_aum_bar.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    bluestock_layout(fig_aum_bar)
    page1_bar = OUTPUT_DIR / "page1_aum_by_amc.png"
    fig_aum_bar.write_image(str(page1_bar), width=1400, height=700)
    fig_aum_bar.write_html(str(OUTPUT_DIR / "page1_aum_by_amc.html"), include_plotlyjs="cdn")

    return [page1_kpi, page1_trend, page1_bar]


def page2_fund_performance(data: dict[str, pd.DataFrame]) -> list[Path]:
    scheme_perf = data["scheme_perf"].copy()
    scorecard = data["fund_scorecard"].copy()
    scorecard = scorecard.merge(
        data["fund_master"][['amfi_code', 'fund_house']],
        on='amfi_code',
        how='left',
    )
    scorecard = scorecard.sort_values("fund_score", ascending=False).head(15)
    scheme_perf["size_aum"] = scheme_perf["aum_crore"].fillna(0) / scheme_perf["aum_crore"].max() * 60 + 15

    fig_scatter = px.scatter(
        scheme_perf,
        x="return_3yr_pct",
        y="std_dev_ann_pct",
        size="size_aum",
        color="category",
        hover_name="scheme_name",
        hover_data={"aum_crore": True, "return_3yr_pct": True, "std_dev_ann_pct": True, "beta": True},
        title="Fund Performance: Return vs Risk (3yr Return vs StdDev)",
        labels={"return_3yr_pct": "3Y Return (%)", "std_dev_ann_pct": "Annualized StdDev (%)"},
    )
    bluestock_layout(fig_scatter)
    page2_scatter = OUTPUT_DIR / "page2_return_vs_risk.png"
    fig_scatter.write_image(str(page2_scatter), width=1400, height=800)
    fig_scatter.write_html(str(OUTPUT_DIR / "page2_return_vs_risk.html"), include_plotlyjs="cdn")

    table = go.Figure(data=[
        go.Table(
            header=dict(values=["Scheme", "Fund House", "Fund Score", "3Y CAGR (%)", "Sharpe", "Alpha (%)", "Expense Ratio (%)", "Max Drawdown (%)"],
                        fill_color="#0e4d92", font=dict(color="white", size=12)),
            cells=dict(values=[
                scorecard["scheme_name"],
                scorecard["fund_house"],
                scorecard["fund_score"].round(2),
                scorecard["3yr_cagr_pct"].round(2),
                scorecard["sharpe_ratio"].round(2),
                scorecard["alpha_pct"].round(2),
                scorecard["expense_ratio_pct"].round(2),
                scorecard["max_drawdown_pct"].round(2),
            ], fill_color="#f8f9fb", align="left", font=dict(color="#0d1b33", size=11))
        )
    ])
    table.update_layout(title_text="Top 15 Funds: Sortable Scorecard Snapshot", height=700)
    fig_table = table
    page2_table = OUTPUT_DIR / "page2_scorecard_table.png"
    fig_table.write_image(str(page2_table), width=1600, height=700)
    fig_table.write_html(str(OUTPUT_DIR / "page2_scorecard_table.html"), include_plotlyjs="cdn")

    top_schemes = scorecard["amfi_code"].tolist()[:3]
    nav_history = data["nav_history"].copy()
    benchmark = data["benchmark"].copy()
    benchmark = benchmark[benchmark["index_name"] == "NIFTY50"].copy()
    nav_plot = nav_history[nav_history["amfi_code"].isin(top_schemes)].copy()
    nav_plot = nav_plot.merge(data["fund_master"][["amfi_code", "scheme_name"]], on="amfi_code", how="left")
    fig_nav = go.Figure()
    for code in top_schemes:
        scheme_name = nav_plot.loc[nav_plot["amfi_code"] == code, "scheme_name"].iloc[0] # type: ignore
        subset = nav_plot[nav_plot["amfi_code"] == code]
        fig_nav.add_trace(go.Scatter(x=subset["date"], y=subset["nav"], mode="lines", name=scheme_name))
    fig_nav.add_trace(go.Scatter(x=benchmark["date"], y=benchmark["close_value"], mode="lines", name="NIFTY50", line=dict(dash="dash", width=3)))
    fig_nav.update_layout(title="NAV Line vs NIFTY50 Benchmark", xaxis_title="Date", yaxis_title="Value")
    bluestock_layout(fig_nav)
    page2_nav = OUTPUT_DIR / "page2_nav_vs_benchmark.png"
    fig_nav.write_image(str(page2_nav), width=1400, height=800)
    fig_nav.write_html(str(OUTPUT_DIR / "page2_nav_vs_benchmark.html"), include_plotlyjs="cdn")

    return [page2_scatter, page2_table, page2_nav]


def page3_investor_analytics(data: dict[str, pd.DataFrame]) -> list[Path]:
    transactions = data["transactions"].copy()
    transactions["month"] = transactions["transaction_date"].dt.to_period("M").dt.to_timestamp()

    amount_by_state = transactions.groupby("state", as_index=False)["amount_inr"].sum().sort_values("amount_inr", ascending=False) # type: ignore
    fig_state = px.bar(
        amount_by_state,
        x="state",
        y="amount_inr",
        title="Transaction Amount by State",
        labels={"amount_inr": "Amount (INR)", "state": "State"},
    )
    bluestock_layout(fig_state)
    fig_state.update_layout(xaxis_tickangle=-45)
    page3_state = OUTPUT_DIR / "page3_amount_by_state.png"
    fig_state.write_image(str(page3_state), width=1400, height=700)
    fig_state.write_html(str(OUTPUT_DIR / "page3_amount_by_state.html"), include_plotlyjs="cdn")

    type_counts = transactions["transaction_type"].value_counts().reset_index()
    type_counts.columns = ["transaction_type", "count"]
    fig_donut = px.pie(
        type_counts,
        names="transaction_type",
        values="count",
        hole=0.45,
        title="Transaction Type Split: SIP / Lumpsum / Redemption",
        color_discrete_sequence=BLUESTOCK_COLORS,
    )
    bluestock_layout(fig_donut)
    page3_donut = OUTPUT_DIR / "page3_transaction_type_split.png"
    fig_donut.write_image(str(page3_donut), width=900, height=700)
    fig_donut.write_html(str(OUTPUT_DIR / "page3_transaction_type_split.html"), include_plotlyjs="cdn")

    sip_transactions = transactions[transactions["transaction_type"].str.upper() == "SIP"].copy()
    avg_sip_by_age = sip_transactions.groupby("age_group", as_index=False)["amount_inr"].mean().sort_values("amount_inr", ascending=False) # type: ignore
    fig_age = px.bar(
        avg_sip_by_age,
        x="age_group",
        y="amount_inr",
        title="Average SIP Transaction Amount by Age Group",
        labels={"amount_inr": "Avg SIP Amount (INR)", "age_group": "Age Group"},
    )
    bluestock_layout(fig_age)
    page3_age = OUTPUT_DIR / "page3_avg_sip_by_age_group.png"
    fig_age.write_image(str(page3_age), width=1400, height=700)
    fig_age.write_html(str(OUTPUT_DIR / "page3_avg_sip_by_age_group.html"), include_plotlyjs="cdn")

    monthly_volume = transactions.groupby("month", as_index=False).size().rename(columns={"size": "transaction_count"})
    fig_vol = px.line(
        monthly_volume,
        x="month",
        y="transaction_count",
        title="Monthly Transaction Volume (Count)",
        markers=True,
        labels={"month": "Month", "transaction_count": "Transactions"},
    )
    bluestock_layout(fig_vol)
    page3_volume = OUTPUT_DIR / "page3_transaction_volume.png"
    fig_vol.write_image(str(page3_volume), width=1400, height=700)
    fig_vol.write_html(str(OUTPUT_DIR / "page3_transaction_volume.html"), include_plotlyjs="cdn")

    return [page3_state, page3_donut, page3_age, page3_volume]


def page4_sip_market_trends(data: dict[str, pd.DataFrame]) -> list[Path]:
    sip = data["sip_inflows"].copy()
    sip["month"] = pd.to_datetime(sip["month"])
    benchmark = data["benchmark"].copy()
    nifty = benchmark[benchmark["index_name"] == "NIFTY50"].copy()

    fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
    fig_dual.add_trace(
        go.Bar(x=sip["month"], y=sip["sip_inflow_crore"], name="SIP Inflow (Cr)", marker_color=BLUESTOCK_COLORS[0]),
        secondary_y=False,
    )
    fig_dual.add_trace(
        go.Scatter(x=nifty["date"], y=nifty["close_value"], name="NIFTY50", line=dict(color=BLUESTOCK_COLORS[1], width=3)),
        secondary_y=True,
    )
    fig_dual.update_layout(title="SIP Inflow vs NIFTY50 (2022–2025)")
    fig_dual.update_xaxes(title_text="Month")
    fig_dual.update_yaxes(title_text="SIP Inflow (Cr)", secondary_y=False)
    fig_dual.update_yaxes(title_text="NIFTY50 Index", secondary_y=True)
    bluestock_layout(fig_dual)
    page4_dual = OUTPUT_DIR / "page4_sip_nifty_trend.png"
    fig_dual.write_image(str(page4_dual), width=1500, height=800)
    fig_dual.write_html(str(OUTPUT_DIR / "page4_sip_nifty_trend.html"), include_plotlyjs="cdn")

    cat = data["category_inflows"].copy()
    cat["month"] = pd.to_datetime(cat["month"])
    heatmap_data = cat.pivot(index="category", columns="month", values="net_inflow_crore").fillna(0)
    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=[d.strftime("%Y-%m") for d in heatmap_data.columns], # type: ignore
            y=heatmap_data.index,
            colorscale="Blues",
            hovertemplate="%{y}<br>%{x}: %{z:.0f} Cr<extra></extra>",
        )
    )
    fig_heatmap.update_layout(title="Category Inflow Heatmap", xaxis_title="Month", yaxis_title="Category")
    bluestock_layout(fig_heatmap)
    page4_heatmap = OUTPUT_DIR / "page4_category_inflow_heatmap.png"
    fig_heatmap.write_image(str(page4_heatmap), width=1500, height=900)
    fig_heatmap.write_html(str(OUTPUT_DIR / "page4_category_inflow_heatmap.html"), include_plotlyjs="cdn")

    fy25_start = pd.Timestamp("2024-04-01")
    fy25_end = pd.Timestamp("2025-03-31")
    fy25 = cat[(cat["month"] >= fy25_start) & (cat["month"] <= fy25_end)].copy()
    top5 = (
        fy25.groupby("category", as_index=False)["net_inflow_crore"].sum()
        .sort_values("net_inflow_crore", ascending=False) # type: ignore
        .head(5)
    )
    fig_top5 = px.bar(
        top5,
        x="category",
        y="net_inflow_crore",
        title="Top 5 Categories by Net Inflow FY25",
        labels={"net_inflow_crore": "Net Inflow (Cr)", "category": "Category"},
        color="category",
    )
    bluestock_layout(fig_top5)
    page4_top5 = OUTPUT_DIR / "page4_top5_categories_fy25.png"
    fig_top5.write_image(str(page4_top5), width=1400, height=700)
    fig_top5.write_html(str(OUTPUT_DIR / "page4_top5_categories_fy25.html"), include_plotlyjs="cdn")

    return [page4_dual, page4_heatmap, page4_top5]


def build_html_portal(image_paths: list[Path]) -> Path:
    sections = [
        ("Industry Overview", [image_paths[0], image_paths[1], image_paths[2]]),
        ("Fund Performance", [image_paths[3], image_paths[4], image_paths[5]]),
        ("Investor Analytics", [image_paths[6], image_paths[7], image_paths[8], image_paths[9]]),
        ("SIP & Market Trends", [image_paths[10], image_paths[11], image_paths[12]]),
    ]

    html_blocks = [
        "<html><head><meta charset='utf-8'><title>Bluestock Dashboard</title>"
        "<style>body{font-family:Arial,sans-serif;background:#f4f6f9;color:#0d1b33;margin:0;padding:0;}"
        "h1{padding:24px 40px 0 40px;}h2{color:#0e4d92;padding:18px 40px 0 40px;}"
        ".section{padding:0 40px 40px 40px;}img{max-width:100%;border:1px solid #e5e8eb;border-radius:8px;margin-bottom:24px;}"
        "</style></head><body><h1>Bluestock Mutual Fund Dashboard</h1>"
        "<p style='padding:0 40px 24px 40px;max-width:900px;'>This report captures the Day 5 dashboard analysis using cleaned mutual fund data. It includes industry KPIs, fund performance analytics, investor transaction insights, and SIP/market trend visualizations.</p>"
    ]

    for title, imgs in sections:
        html_blocks.append(f"<div class='section'><h2>{title}</h2>")
        for img in imgs:
            html_blocks.append(f"<img src='{img.name}' alt='{title}'>")
        html_blocks.append("</div>")
    html_blocks.append("</body></html>")

    DASHBOARD_HTML.write_text("\n".join(html_blocks), encoding="utf-8")
    return DASHBOARD_HTML


def export_pdf(image_paths: list[Path]) -> Path:
    pdf_path = DASHBOARD_PDF
    try:
        import img2pdf
    except ImportError:
        print("Warning: img2pdf is not installed. Skipping PDF export.")
        return pdf_path

    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert([str(path) for path in image_paths])) # type: ignore
    return pdf_path


def main() -> None:
    data = load_cleaned_data()
    page1 = page1_overview(data)
    page2 = page2_fund_performance(data)
    page3 = page3_investor_analytics(data)
    page4 = page4_sip_market_trends(data)
    all_pages = page1 + page2 + page3 + page4
    html_path = build_html_portal(all_pages)
    pdf_path = export_pdf(all_pages)
    print(f"Generated dashboard HTML: {html_path}")
    print(f"Generated dashboard PDF: {pdf_path}")
    print(f"Generated PNG outputs in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
