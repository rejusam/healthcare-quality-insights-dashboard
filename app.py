"""
Healthcare Quality & Safety Insights Dashboard
===============================================
Te Whatu Ora Waitematā - Quality and Risk Analytics

Author: Reju Sam John, PhD
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose
from io import BytesIO
import os

# ── Page Config ──
st.set_page_config(
    page_title="Quality & Safety Insights | HNZ Waitematā",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ──
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem; font-weight: 700;
        color: #00838F; margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem; color: #555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem; border-radius: 8px;
        border-left: 4px solid #00838F;
    }
    .stMetric > div { background-color: #f8f9fa; border-radius: 8px; padding: 8px; }
</style>
""", unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


# ── Data Loading ──
@st.cache_data
def load_data():
    ae = pd.read_csv(os.path.join(DATA_DIR, "adverse_events.csv"), parse_dates=["event_date"])
    comp = pd.read_csv(os.path.join(DATA_DIR, "complaints.csv"), parse_dates=["received_date"])
    qi = pd.read_csv(os.path.join(DATA_DIR, "quality_indicators.csv"))
    eq = pd.read_csv(os.path.join(DATA_DIR, "equity_indicators.csv"))
    return ae, comp, qi, eq


ae_df, comp_df, qi_df, eq_df = load_data()

# ── Sidebar ──
st.sidebar.markdown("### 🏥 Quality & Safety Insights")
st.sidebar.markdown("**Te Whatu Ora Waitematā**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "📊 Executive Summary",
        "⚠️ Adverse Events Analysis",
        "📝 Complaints Analysis",
        "📈 Quality Indicators & Trends",
        "🤝 Health Equity (Te Tiriti)",
        "🔬 Statistical Deep Dive",
        "📋 Report Generator",
    ],
)

# Shared filters
st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")
year_options = sorted(ae_df["year"].unique())
selected_years = st.sidebar.multiselect("Year(s)", year_options, default=year_options)
selected_facilities = st.sidebar.multiselect(
    "Facility", ae_df["facility"].unique(), default=ae_df["facility"].unique()
)

# Apply filters
ae_filtered = ae_df[
    (ae_df["year"].isin(selected_years)) & (ae_df["facility"].isin(selected_facilities))
]
comp_filtered = comp_df[
    (comp_df["year"].isin(selected_years)) & (comp_df["facility"].isin(selected_facilities))
]
qi_filtered = qi_df[
    (qi_df["month"].str[:4].astype(int).isin(selected_years))
    & (qi_df["facility"].isin(selected_facilities))
]

COLORS = px.colors.qualitative.Vivid


# ═══════════════════════════════════════════════════════
# PAGE: Executive Summary
# ═══════════════════════════════════════════════════════
if page == "📊 Executive Summary":
    st.markdown('<p class="main-header">Executive Summary Dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Key quality and safety metrics at a glance '
        '| Data: Simulated healthcare quality data</p>',
        unsafe_allow_html=True,
    )

    # KPI row
    col1, col2, col3, col4, col5 = st.columns(5)

    total_ae = len(ae_filtered)
    sac1_count = len(ae_filtered[ae_filtered["severity"] == "SAC 1 - Severe"])
    total_comp = len(comp_filtered)
    open_ae = len(ae_filtered[ae_filtered["status"] == "Open"])
    avg_close = ae_filtered["days_to_close"].mean()

    col1.metric("Total Adverse Events", f"{total_ae:,}", help="All reported adverse events")
    col2.metric("SAC 1 (Severe)", sac1_count, help="Severity Assessment Code 1 events")
    col3.metric("Total Complaints", f"{total_comp:,}")
    col4.metric("Open Events", open_ae)
    col5.metric("Avg Days to Close", f"{avg_close:.0f}")

    st.markdown("---")

    # Row 2: Charts
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Adverse Events Trend (Monthly)")
        monthly_ae = (
            ae_filtered.groupby("month").size().reset_index(name="count").sort_values("month")
        )
        fig = px.line(
            monthly_ae, x="month", y="count",
            labels={"month": "Month", "count": "Event Count"},
        )
        fig.update_layout(height=350, margin=dict(t=20, b=40))
        fig.update_xaxes(tickangle=45, dtick=3)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Events by Severity")
        sev_counts = ae_filtered["severity"].value_counts().reset_index()
        sev_counts.columns = ["severity", "count"]
        fig = px.pie(
            sev_counts, values="count", names="severity",
            color_discrete_sequence=["#d32f2f", "#f57c00", "#fbc02d", "#388e3c"],
        )
        fig.update_layout(height=350, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Row 3
    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.subheader("Top Event Categories")
        cat_counts = (
            ae_filtered["event_category"].value_counts().head(8).reset_index()
        )
        cat_counts.columns = ["category", "count"]
        fig = px.bar(
            cat_counts, x="count", y="category", orientation="h",
            color="count", color_continuous_scale="Teal",
        )
        fig.update_layout(height=350, margin=dict(t=20, b=20), showlegend=False)
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_right2:
        st.subheader("Events by Facility")
        fac_counts = ae_filtered["facility"].value_counts().reset_index()
        fac_counts.columns = ["facility", "count"]
        fig = px.bar(
            fac_counts, x="facility", y="count",
            color="facility", color_discrete_sequence=COLORS,
        )
        fig.update_layout(height=350, margin=dict(t=20, b=20), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap: Events by Service x Category
    st.subheader("Event Heatmap: Service vs Category")
    heatmap_data = pd.crosstab(ae_filtered["service"], ae_filtered["event_category"])
    fig = px.imshow(
        heatmap_data, aspect="auto", color_continuous_scale="YlOrRd",
        labels={"x": "Event Category", "y": "Service", "color": "Count"},
    )
    fig.update_layout(height=450, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════
# PAGE: Adverse Events Analysis
# ═══════════════════════════════════════════════════════
elif page == "⚠️ Adverse Events Analysis":
    st.markdown('<p class="main-header">Adverse Events Analysis</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Detailed analysis of patient safety events with trend '
        'identification and benchmarking</p>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["📈 Trends", "👥 Demographics", "⏱️ Timeliness"])

    with tab1:
        st.subheader("Monthly Trend by Severity")
        monthly_sev = (
            ae_filtered.groupby(["month", "severity"]).size()
            .reset_index(name="count").sort_values("month")
        )
        fig = px.area(
            monthly_sev, x="month", y="count", color="severity",
            color_discrete_sequence=["#d32f2f", "#f57c00", "#fbc02d", "#388e3c"],
        )
        fig.update_layout(height=400, margin=dict(t=20, b=40))
        fig.update_xaxes(tickangle=45, dtick=3)
        st.plotly_chart(fig, use_container_width=True)

        # Year-over-Year comparison
        st.subheader("Year-over-Year Comparison by Category")
        yoy = ae_filtered.groupby(["year", "event_category"]).size().reset_index(name="count")
        fig = px.bar(
            yoy, x="event_category", y="count", color="year",
            barmode="group", color_discrete_sequence=COLORS,
        )
        fig.update_layout(height=400, margin=dict(t=20, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Age Distribution")
            fig = px.histogram(
                ae_filtered, x="patient_age", nbins=30,
                color="severity",
                color_discrete_sequence=["#d32f2f", "#f57c00", "#fbc02d", "#388e3c"],
                labels={"patient_age": "Patient Age"},
            )
            fig.update_layout(height=400, margin=dict(t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Events by Ethnicity")
            eth_counts = ae_filtered["patient_ethnicity"].value_counts().reset_index()
            eth_counts.columns = ["ethnicity", "count"]
            fig = px.bar(
                eth_counts, x="ethnicity", y="count",
                color="ethnicity", color_discrete_sequence=COLORS,
            )
            fig.update_layout(height=400, margin=dict(t=20, b=20), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        # Age-category relationship
        st.subheader("Event Category by Age Group")
        ae_temp = ae_filtered.copy()
        ae_temp["age_group"] = pd.cut(
            ae_temp["patient_age"],
            bins=[0, 18, 40, 65, 80, 100],
            labels=["0-18", "19-40", "41-65", "66-80", "81+"],
        )
        age_cat = ae_temp.groupby(["age_group", "event_category"]).size().reset_index(name="count")
        fig = px.bar(
            age_cat, x="age_group", y="count", color="event_category",
            color_discrete_sequence=COLORS,
        )
        fig.update_layout(height=400, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Days to Close Distribution by Severity")
        fig = px.box(
            ae_filtered, x="severity", y="days_to_close",
            color="severity",
            color_discrete_sequence=["#d32f2f", "#f57c00", "#fbc02d", "#388e3c"],
        )
        fig.update_layout(height=400, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

        # Timeliness trend
        st.subheader("Average Days to Close (Monthly Trend)")
        close_trend = (
            ae_filtered.groupby("month")["days_to_close"]
            .mean().reset_index().sort_values("month")
        )
        fig = px.line(close_trend, x="month", y="days_to_close")
        fig.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Target: 30 days")
        fig.update_layout(height=350, margin=dict(t=20, b=40))
        fig.update_xaxes(tickangle=45, dtick=3)
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════
# PAGE: Complaints Analysis
# ═══════════════════════════════════════════════════════
elif page == "📝 Complaints Analysis":
    st.markdown('<p class="main-header">Patient Complaints Analysis</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Tracking complaint trends, resolution times, '
        'and identifying improvement opportunities</p>',
        unsafe_allow_html=True,
    )

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    resolved = comp_filtered[comp_filtered["status"] == "Resolved"]
    within_20 = len(resolved[resolved["resolution_days"] <= 20]) / max(len(resolved), 1) * 100
    escalated_pct = comp_filtered["escalated"].mean() * 100

    c1.metric("Total Complaints", len(comp_filtered))
    c2.metric("Avg Resolution (days)", f"{comp_filtered['resolution_days'].mean():.0f}")
    c3.metric("Resolved ≤ 20 days", f"{within_20:.0f}%")
    c4.metric("Escalated", f"{escalated_pct:.1f}%")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Complaints by Category")
        cat_counts = comp_filtered["category"].value_counts().reset_index()
        cat_counts.columns = ["category", "count"]
        fig = px.pie(cat_counts, values="count", names="category", color_discrete_sequence=COLORS)
        fig.update_layout(height=380, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Monthly Complaint Trend")
        monthly_comp = (
            comp_filtered.groupby("month").size().reset_index(name="count").sort_values("month")
        )
        fig = px.line(monthly_comp, x="month", y="count")
        fig.update_layout(height=380, margin=dict(t=20, b=40))
        fig.update_xaxes(tickangle=45, dtick=3)
        st.plotly_chart(fig, use_container_width=True)

    # Resolution time by category
    st.subheader("Resolution Time by Category")
    fig = px.box(
        comp_filtered, x="category", y="resolution_days",
        color="category", color_discrete_sequence=COLORS,
    )
    fig.add_hline(y=20, line_dash="dash", line_color="red", annotation_text="20-day target")
    fig.update_layout(height=400, margin=dict(t=20), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Complaints by facility and category
    st.subheader("Facility vs Complaint Category")
    fac_cat = pd.crosstab(comp_filtered["facility"], comp_filtered["category"])
    fig = px.imshow(
        fac_cat, aspect="auto", color_continuous_scale="Blues",
        labels={"x": "Category", "y": "Facility", "color": "Count"},
    )
    fig.update_layout(height=350, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════
# PAGE: Quality Indicators & Trends
# ═══════════════════════════════════════════════════════
elif page == "📈 Quality Indicators & Trends":
    st.markdown('<p class="main-header">Quality Indicators & KPI Tracking</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Monitoring key quality indicators against targets '
        'with trend analysis and benchmarking</p>',
        unsafe_allow_html=True,
    )

    indicators = qi_filtered["indicator"].unique()
    selected_indicator = st.selectbox("Select Indicator", indicators)

    ind_data = qi_filtered[qi_filtered["indicator"] == selected_indicator]
    target_val = ind_data["target"].iloc[0]

    # Trend chart with target line
    st.subheader(f"Trend: {selected_indicator}")
    fig = px.line(
        ind_data, x="month", y="value", color="facility",
        color_discrete_sequence=COLORS,
    )
    fig.add_hline(
        y=target_val, line_dash="dash", line_color="red",
        annotation_text=f"Target: {target_val}",
    )
    fig.update_layout(height=450, margin=dict(t=20, b=40))
    fig.update_xaxes(tickangle=45, dtick=3)
    st.plotly_chart(fig, use_container_width=True)

    # Benchmarking table
    st.subheader("Facility Benchmarking")
    benchmark = (
        ind_data.groupby("facility")["value"]
        .agg(["mean", "std", "min", "max"])
        .round(2)
        .reset_index()
    )
    benchmark.columns = ["Facility", "Mean", "Std Dev", "Min", "Max"]
    benchmark["Target"] = target_val

    # Determine if lower or higher is better
    lower_is_better = any(
        kw in selected_indicator.lower() for kw in ["error", "fall", "injury", "hai", "rate"]
    )
    if lower_is_better:
        benchmark["Status"] = benchmark["Mean"].apply(
            lambda x: "✅ Meeting Target" if x <= target_val else "⚠️ Above Target"
        )
    else:
        benchmark["Status"] = benchmark["Mean"].apply(
            lambda x: "✅ Meeting Target" if x >= target_val else "⚠️ Below Target"
        )

    st.dataframe(benchmark, use_container_width=True, hide_index=True)

    # Statistical Process Control (SPC) chart
    st.subheader("Statistical Process Control (SPC) Chart")
    overall = ind_data.groupby("month")["value"].mean().reset_index().sort_values("month")
    mean_val = overall["value"].mean()
    std_val = overall["value"].std()
    ucl = mean_val + 3 * std_val
    lcl = mean_val - 3 * std_val

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=overall["month"], y=overall["value"],
        mode="lines+markers", name="Value", line=dict(color="#00838F"),
    ))
    fig.add_hline(y=mean_val, line_dash="solid", line_color="green",
                  annotation_text=f"Mean: {mean_val:.1f}")
    fig.add_hline(y=ucl, line_dash="dash", line_color="red",
                  annotation_text=f"UCL: {ucl:.1f}")
    fig.add_hline(y=lcl, line_dash="dash", line_color="red",
                  annotation_text=f"LCL: {lcl:.1f}")
    fig.update_layout(height=400, margin=dict(t=20, b=40))
    fig.update_xaxes(tickangle=45, dtick=3)
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "**SPC Interpretation:** Points outside the control limits (UCL/LCL) "
        "indicate special cause variation requiring investigation. Points within "
        "limits represent common cause variation inherent to the process."
    )


# ═══════════════════════════════════════════════════════
# PAGE: Health Equity
# ═══════════════════════════════════════════════════════
elif page == "🤝 Health Equity (Te Tiriti)":
    st.markdown('<p class="main-header">Health Equity Analysis</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Supporting equitable health outcomes for Māori and all '
        'communities | Te Tiriti o Waitangi commitment</p>',
        unsafe_allow_html=True,
    )

    eq_indicators = eq_df["indicator"].unique()
    selected_eq = st.selectbox("Select Equity Indicator", eq_indicators)

    eq_data = eq_df[eq_df["indicator"] == selected_eq]

    # Trend by ethnicity
    st.subheader(f"Trend by Ethnicity: {selected_eq}")
    fig = px.line(
        eq_data, x="month", y="value", color="ethnicity",
        color_discrete_sequence=COLORS,
    )
    fig.update_layout(height=450, margin=dict(t=20, b=40))
    fig.update_xaxes(tickangle=45, dtick=6)
    st.plotly_chart(fig, use_container_width=True)

    # Gap analysis
    st.subheader("Equity Gap Analysis")
    latest_6m = eq_data[eq_data["month"] >= "2025-07"]
    gap_summary = latest_6m.groupby("ethnicity")["value"].mean().reset_index()
    gap_summary.columns = ["Ethnicity", "Average Value"]
    nz_euro_val = gap_summary[gap_summary["Ethnicity"] == "NZ European"]["Average Value"].values[0]
    gap_summary["Gap vs NZ European"] = (gap_summary["Average Value"] - nz_euro_val).round(1)
    gap_summary["Average Value"] = gap_summary["Average Value"].round(1)

    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(gap_summary, use_container_width=True, hide_index=True)

    with col2:
        fig = px.bar(
            gap_summary, x="Ethnicity", y="Average Value",
            color="Ethnicity", color_discrete_sequence=COLORS,
        )
        fig.update_layout(height=350, margin=dict(t=20), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Adverse events by ethnicity
    st.subheader("Adverse Events Rate by Ethnicity")
    ae_eth = ae_filtered.groupby("patient_ethnicity").agg(
        total_events=("event_id", "count"),
        avg_severity=("days_to_close", "mean"),
        sac1_count=("severity", lambda x: (x == "SAC 1 - Severe").sum()),
    ).reset_index()
    ae_eth.columns = ["Ethnicity", "Total Events", "Avg Days to Close", "SAC 1 Count"]
    ae_eth = ae_eth.round(1)
    st.dataframe(ae_eth, use_container_width=True, hide_index=True)

    st.info(
        "**Note:** Equity analysis supports HNZ Waitematā's commitment under Te Tiriti o "
        "Waitangi to achieve equitable health outcomes for Māori. Disparities identified "
        "here should inform targeted quality improvement initiatives."
    )


# ═══════════════════════════════════════════════════════
# PAGE: Statistical Deep Dive
# ═══════════════════════════════════════════════════════
elif page == "🔬 Statistical Deep Dive":
    st.markdown('<p class="main-header">Statistical Analysis</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Hypothesis testing, correlation analysis, and time series '
        'decomposition to inform evidence-based decisions</p>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs([
        "🧪 Hypothesis Testing", "📊 Correlation Analysis", "📉 Time Series Decomposition"
    ])

    with tab1:
        st.subheader("1. Are SAC 1 events taking longer to close? (Mann-Whitney U Test)")
        sac1_close = ae_filtered[ae_filtered["severity"] == "SAC 1 - Severe"]["days_to_close"]
        other_close = ae_filtered[ae_filtered["severity"] != "SAC 1 - Severe"]["days_to_close"]

        if len(sac1_close) > 1 and len(other_close) > 1:
            u_stat, p_value = stats.mannwhitneyu(sac1_close, other_close, alternative="greater")
            col1, col2, col3 = st.columns(3)
            col1.metric("U Statistic", f"{u_stat:,.0f}")
            col2.metric("p-value", f"{p_value:.4f}")
            col3.metric("Significant (α=0.05)?", "Yes ✅" if p_value < 0.05 else "No ❌")

            st.markdown(
                f"**Interpretation:** SAC 1 events have a median closure time of "
                f"**{sac1_close.median():.0f} days** compared to **{other_close.median():.0f} days** "
                f"for other severities. "
                f"{'This difference is statistically significant.' if p_value < 0.05 else 'This difference is not statistically significant.'}"
            )

            fig = go.Figure()
            fig.add_trace(go.Histogram(x=sac1_close, name="SAC 1", opacity=0.7, marker_color="#d32f2f"))
            fig.add_trace(go.Histogram(x=other_close, name="Other", opacity=0.7, marker_color="#388e3c"))
            fig.update_layout(barmode="overlay", height=350, margin=dict(t=20),
                              xaxis_title="Days to Close", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        st.subheader("2. Does complaint category affect resolution time? (Kruskal-Wallis Test)")
        groups = [
            group["resolution_days"].values
            for _, group in comp_filtered.groupby("category")
        ]
        if len(groups) > 1:
            h_stat, p_val_kw = stats.kruskal(*groups)
            col1, col2, col3 = st.columns(3)
            col1.metric("H Statistic", f"{h_stat:.2f}")
            col2.metric("p-value", f"{p_val_kw:.4f}")
            col3.metric("Significant (α=0.05)?", "Yes ✅" if p_val_kw < 0.05 else "No ❌")
            st.markdown(
                f"**Interpretation:** "
                f"{'Complaint category significantly affects resolution time.' if p_val_kw < 0.05 else 'No significant difference in resolution time across complaint categories.'} "
                f"This informs resource allocation for complaint handling."
            )

        st.markdown("---")

        st.subheader("3. Chi-Square Test: Event Severity vs Facility")
        contingency = pd.crosstab(ae_filtered["facility"], ae_filtered["severity"])
        chi2, p_val_chi, dof, expected = stats.chi2_contingency(contingency)
        col1, col2, col3 = st.columns(3)
        col1.metric("Chi-Square", f"{chi2:.2f}")
        col2.metric("p-value", f"{p_val_chi:.4f}")
        col3.metric("Degrees of Freedom", dof)
        st.markdown(
            f"**Interpretation:** "
            f"{'The distribution of event severity differs significantly across facilities.' if p_val_chi < 0.05 else 'Event severity distribution is consistent across facilities.'}"
        )

    with tab2:
        st.subheader("Correlation: Patient Age vs Days to Close")
        corr, p_corr = stats.spearmanr(ae_filtered["patient_age"], ae_filtered["days_to_close"])

        col1, col2 = st.columns(2)
        col1.metric("Spearman Correlation", f"{corr:.3f}")
        col2.metric("p-value", f"{p_corr:.4f}")

        # Scatter with regression
        fig = px.scatter(
            ae_filtered.sample(min(500, len(ae_filtered)), random_state=42),
            x="patient_age", y="days_to_close",
            color="severity", trendline="ols",
            color_discrete_sequence=["#d32f2f", "#f57c00", "#fbc02d", "#388e3c"],
            labels={"patient_age": "Patient Age", "days_to_close": "Days to Close"},
        )
        fig.update_layout(height=450, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

        # Correlation matrix for numeric fields
        st.subheader("Correlation Matrix")
        numeric_cols = ae_filtered[["patient_age", "days_to_close"]].copy()
        numeric_cols["severity_code"] = ae_filtered["severity"].map({
            "SAC 1 - Severe": 1, "SAC 2 - Major": 2,
            "SAC 3 - Moderate": 3, "SAC 4 - Minor": 4,
        })
        corr_matrix = numeric_cols.corr(method="spearman")
        fig = px.imshow(
            corr_matrix, text_auto=".2f", aspect="auto",
            color_continuous_scale="RdBu_r",
        )
        fig.update_layout(height=350, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Time Series Decomposition of Adverse Events")
        monthly_ts = (
            ae_filtered.groupby("month").size().reset_index(name="count").sort_values("month")
        )
        monthly_ts.index = pd.to_datetime(monthly_ts["month"])
        monthly_ts = monthly_ts["count"]

        if len(monthly_ts) >= 24:
            decomp = seasonal_decompose(monthly_ts, model="additive", period=12)

            fig = make_subplots(
                rows=4, cols=1, shared_xaxes=True,
                subplot_titles=["Observed", "Trend", "Seasonal", "Residual"],
                vertical_spacing=0.06,
            )
            fig.add_trace(go.Scatter(x=decomp.observed.index, y=decomp.observed, mode="lines",
                                     line=dict(color="#00838F")), row=1, col=1)
            fig.add_trace(go.Scatter(x=decomp.trend.index, y=decomp.trend, mode="lines",
                                     line=dict(color="#e65100")), row=2, col=1)
            fig.add_trace(go.Scatter(x=decomp.seasonal.index, y=decomp.seasonal, mode="lines",
                                     line=dict(color="#1565c0")), row=3, col=1)
            fig.add_trace(go.Scatter(x=decomp.resid.index, y=decomp.resid, mode="lines+markers",
                                     line=dict(color="#6a1b9a")), row=4, col=1)
            fig.update_layout(height=700, showlegend=False, margin=dict(t=40))
            st.plotly_chart(fig, use_container_width=True)

            st.info(
                "**Decomposition reveals:** Trend component shows overall direction, "
                "seasonal component captures recurring patterns (e.g., winter peaks), "
                "and residuals highlight unusual events for investigation."
            )
        else:
            st.warning("Need at least 24 months of data for decomposition. Adjust filters.")


# ═══════════════════════════════════════════════════════
# PAGE: Report Generator
# ═══════════════════════════════════════════════════════
elif page == "📋 Report Generator":
    st.markdown('<p class="main-header">Report Generator</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Generate and export reports for local, regional, '
        'and national reporting requirements</p>',
        unsafe_allow_html=True,
    )

    report_type = st.selectbox("Report Type", [
        "Monthly Quality Summary",
        "Adverse Events Detail",
        "Complaints Summary",
        "Equity Indicators",
        "KPI Benchmarking",
    ])

    if report_type == "Monthly Quality Summary":
        st.subheader("Monthly Quality Summary Report")

        # Summary stats
        summary_data = {
            "Metric": [
                "Total Adverse Events", "SAC 1 Events", "SAC 2 Events",
                "Total Complaints", "Avg Resolution Days (Complaints)",
                "Avg Days to Close (AE)", "Escalated Complaints (%)",
            ],
            "Value": [
                len(ae_filtered),
                len(ae_filtered[ae_filtered["severity"] == "SAC 1 - Severe"]),
                len(ae_filtered[ae_filtered["severity"] == "SAC 2 - Major"]),
                len(comp_filtered),
                f"{comp_filtered['resolution_days'].mean():.1f}",
                f"{ae_filtered['days_to_close'].mean():.1f}",
                f"{comp_filtered['escalated'].mean() * 100:.1f}%",
            ],
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

    elif report_type == "Adverse Events Detail":
        st.subheader("Adverse Events Detailed Report")
        display_cols = [
            "event_id", "event_date", "facility", "service",
            "event_category", "severity", "harm_level",
            "patient_age", "patient_ethnicity", "days_to_close", "status",
        ]
        st.dataframe(
            ae_filtered[display_cols].sort_values("event_date", ascending=False),
            use_container_width=True, hide_index=True,
        )

    elif report_type == "Complaints Summary":
        st.subheader("Complaints Summary Report")
        st.dataframe(
            comp_filtered.sort_values("received_date", ascending=False),
            use_container_width=True, hide_index=True,
        )

    elif report_type == "Equity Indicators":
        st.subheader("Equity Indicators Report")
        eq_pivot = eq_df.pivot_table(
            index=["indicator", "ethnicity"], values="value",
            aggfunc=["mean", "std", "min", "max"],
        ).round(2)
        eq_pivot.columns = ["Mean", "Std Dev", "Min", "Max"]
        st.dataframe(eq_pivot, use_container_width=True)

    elif report_type == "KPI Benchmarking":
        st.subheader("KPI Benchmarking Report")
        benchmark_all = (
            qi_filtered.groupby(["indicator", "facility"])["value"]
            .agg(["mean", "std", "min", "max"])
            .round(2)
            .reset_index()
        )
        benchmark_all.columns = ["Indicator", "Facility", "Mean", "Std Dev", "Min", "Max"]
        st.dataframe(benchmark_all, use_container_width=True, hide_index=True)

    # Export
    st.markdown("---")
    st.subheader("Export Data")

    col1, col2 = st.columns(2)
    with col1:
        csv_data = ae_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Adverse Events (CSV)",
            csv_data, "adverse_events_export.csv", "text/csv",
        )
    with col2:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            ae_filtered.to_excel(writer, sheet_name="Adverse Events", index=False)
            comp_filtered.to_excel(writer, sheet_name="Complaints", index=False)
        st.download_button(
            "📥 Download Full Report (Excel)",
            buffer.getvalue(),
            "quality_report_export.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# ── Footer ──
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Built by:** Reju Sam John, PhD  \n"
    "**Data:** Simulated quality data  \n"
    "**Stack:** Python, Streamlit, Plotly, SciPy"
)
