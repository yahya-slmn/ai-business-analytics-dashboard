import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE CONFIG
st.set_page_config(
    page_title="AI Business Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# STYLING
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #050816 0%, #081120 40%, #0b1d35 100%);
        color: #e2e2e2;
    }

    html, body, [class*="css"] {
        color: #e2e2e2 !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        border-right: 1px solid rgba(45,138,184,0.25);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label {
        color: #e2e2e2 !important;
    }

    div[data-testid="metric-container"] {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(45,138,184,0.25);
        padding: 18px;
        border-radius: 18px;
        box-shadow: 0 0 20px rgba(45,138,184,0.08);
    }

    .stSelectbox div[data-baseweb="select"],
    .stMultiSelect div[data-baseweb="select"] {
        background-color: #0f172a;
        border-radius: 12px;
    }

    .stDateInput {
        background-color: #0f172a;
        border-radius: 12px;
    }

    .stDataFrame {
        border-radius: 14px;
        overflow: hidden;
    }

    .stButton button,
    .stDownloadButton button {
        background: linear-gradient(135deg, #2d8ab8, #1f6f96);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
    }

    .stButton button:hover,
    .stDownloadButton button:hover {
        background: linear-gradient(135deg, #3ca3d6, #2d8ab8);
        color: white;
    }

    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    hr {
        border-color: rgba(226,226,226,0.1);
    }

    label, p, span, div {
        color: #e2e2e2 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #bfc9d4 !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    [data-testid="stFileUploader"] {
        color: #e2e2e2 !important;
    }

    @media (max-width: 768px) {
        h1 {
            font-size: 2.4rem !important;
        }

        h2 {
            font-size: 1.8rem !important;
        }

        .block-container {
            padding-top: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        div[data-testid="metric-container"] {
            margin-bottom: 16px !important;
            padding: 16px !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.95rem !important;
            font-weight: 600 !important;
        }

        .stButton button {
            width: 100% !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# TITLE
st.title("AI-Powered Business Analytics Dashboard")
st.write(
    "Analyze sales and profit performance with interactive KPIs, trends, category analysis, and business insights."
)

# FILE UPLOAD
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if "df" not in st.session_state:
    st.session_state.df = None

if st.button("Use Sample Business Dataset"):
    st.session_state.df = pd.read_csv("sample_data/business_sales_dataset.csv")

if uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file)

df = st.session_state.df

if df is None:
    st.info("Upload a CSV file or use the sample dataset to begin analysis.")
    st.stop()

# HELPERS
def format_number(value):
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"${value / 1_000:.2f}K"
    else:
        return f"${value:,.0f}"


def style_chart_layout(fig, title_text, x_title=None, y_title=None, show_axes=True):
    layout = dict(
        height=500,
        plot_bgcolor="rgba(15,23,42,0.75)",
        paper_bgcolor="rgba(15,23,42,0.75)",
        font=dict(color="#e2e2e2"),
        title=dict(
            text=title_text,
            font=dict(color="#ffffff", size=22)
        ),
        legend=dict(
            font=dict(color="#e2e2e2", size=12)
        )
    )

    if show_axes:
        layout["xaxis"] = dict(
            title=dict(
                text=x_title,
                font=dict(color="#e2e2e2")
            ),
            tickfont=dict(color="#e2e2e2"),
            gridcolor="rgba(226,226,226,0.12)"
        )
        layout["yaxis"] = dict(
            title=dict(
                text=y_title,
                font=dict(color="#e2e2e2")
            ),
            tickfont=dict(color="#e2e2e2"),
            gridcolor="rgba(226,226,226,0.12)"
        )

    fig.update_layout(**layout)
    return fig


# DATA PREPARATION
date_cols = [col for col in df.columns if "date" in col.lower()]

if date_cols:
    date_col = date_cols[0]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
else:
    date_col = None

numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

if not numeric_cols:
    st.error("No numeric columns found in the uploaded dataset.")
    st.stop()

priority_metrics = [
    col for col in numeric_cols
    if col.lower() in ["sales", "profit"]
]

kpi_options = priority_metrics if priority_metrics else numeric_cols

categorical_cols = [
    col for col in df.select_dtypes(include=["object"]).columns.tolist()
    if col not in date_cols
]

# SIDEBAR
st.sidebar.header("Dashboard Controls")

selected_value = st.sidebar.selectbox(
    "Select KPI",
    kpi_options
)

filtered_df = df.copy()

# DATE FILTER
if date_col:
    min_date = filtered_df[date_col].min()
    max_date = filtered_df[date_col].max()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date)
    )

    if len(date_range) == 2:
        start_date, end_date = date_range

        filtered_df = filtered_df[
            (filtered_df[date_col] >= pd.to_datetime(start_date)) &
            (filtered_df[date_col] <= pd.to_datetime(end_date))
        ]

# CATEGORY FILTER
if categorical_cols:
    filter_col = st.sidebar.selectbox(
        "Filter Column",
        categorical_cols
    )

    available_values = sorted(
        filtered_df[filter_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_filters = st.sidebar.multiselect(
        f"Select {filter_col.title()}",
        options=available_values,
        default=available_values
    )

    if not selected_filters:
        st.sidebar.warning("Please keep at least one value selected.")
        st.stop()

    filtered_df = filtered_df[
        filtered_df[filter_col].astype(str).isin(selected_filters)
    ]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

display_df = filtered_df.copy()

if date_col:
    display_df[date_col] = display_df[date_col].dt.strftime("%Y-%m-%d")

# KPI OVERVIEW
st.subheader("Executive KPI Overview")

total_value = filtered_df[selected_value].sum()
avg_value = filtered_df[selected_value].mean()
max_value = filtered_df[selected_value].max()
records_count = filtered_df.shape[0]

sales_col = next((c for c in numeric_cols if c.lower() == "sales"), None)
profit_col = next((c for c in numeric_cols if c.lower() == "profit"), None)

profit_margin = None

if sales_col and profit_col:
    sales_total = filtered_df[sales_col].sum()
    profit_total = filtered_df[profit_col].sum()

    if sales_total != 0:
        profit_margin = (profit_total / sales_total) * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    f"Total {selected_value.title()}",
    format_number(total_value)
)

col2.metric(
    f"Average {selected_value.title()}",
    format_number(avg_value)
)

col3.metric(
    f"Highest {selected_value.title()}",
    format_number(max_value)
)

if profit_margin is not None:
    col4.metric(
        "Profit Margin",
        f"{profit_margin:.2f}%"
    )
else:
    col4.metric(
        "Records",
        f"{records_count:,}"
    )

st.divider()

# DATASET PREVIEW
st.subheader("Dataset Preview")

st.dataframe(
    display_df.head(10),
    use_container_width=True
)

st.divider()

# TREND ANALYSIS
trend_df = None

if date_col:
    st.subheader("Trend Analysis")

    trend_df = filtered_df.copy()

    trend_df["Month"] = (
        trend_df[date_col]
        .dt.to_period("M")
        .astype(str)
    )

    trend_df = (
        trend_df.groupby("Month")[selected_value]
        .sum()
        .reset_index()
    )

    fig_trend = px.line(
        trend_df,
        x="Month",
        y=selected_value,
        markers=True,
        line_shape="spline",
        title=f"{selected_value.title()} Monthly Trend",
        template="plotly_dark"
    )

    fig_trend.update_traces(
        line=dict(
            color="#2d8ab8",
            width=4
        ),
        marker=dict(
            size=9,
            color="#e2e2e2",
            line=dict(
                color="#2d8ab8",
                width=2
            )
        ),
        mode="lines+markers+text",
        text=[format_number(v) for v in trend_df[selected_value]],
        textposition="top center",
        textfont=dict(
            color="#e2e2e2",
            size=12
        )
    )

    style_chart_layout(
        fig_trend,
        title_text=f"{selected_value.title()} Monthly Trend",
        x_title="Month",
        y_title=selected_value.title(),
        show_axes=True
    )

    fig_trend.update_layout(hovermode="x unified")

    st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# CATEGORY PERFORMANCE ANALYSIS
category_summary = None
selected_category = None

if categorical_cols:
    st.subheader("Category Performance Analysis")

    selected_category = st.selectbox(
        "Select Category Column",
        categorical_cols
    )

    category_summary = (
        filtered_df.groupby(selected_category)[selected_value]
        .sum()
        .reset_index()
        .sort_values(by=selected_value, ascending=False)
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_bar = px.bar(
            category_summary,
            x=selected_category,
            y=selected_value,
            title=f"{selected_value.title()} by {selected_category.title()}",
            text_auto=".2s",
            template="plotly_dark",
            color_discrete_sequence=["#2d8ab8"]
        )

        fig_bar.update_traces(
            marker_line_color="#2daab8",
            marker_line_width=1.2,
            opacity=0.9,
            textfont=dict(color="#e2e2e2")
        )

        style_chart_layout(
            fig_bar,
            title_text=f"{selected_value.title()} by {selected_category.title()}",
            x_title=selected_category.title(),
            y_title=selected_value.title(),
            show_axes=True
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    with chart_col2:
        fig_pie = px.pie(
            category_summary,
            names=selected_category,
            values=selected_value,
            title=f"{selected_value.title()} Contribution",
            template="plotly_dark",
            color_discrete_sequence=[
                "#2d8ab8",
                "#4aa3cf",
                "#66b8dd",
                "#8ac9e8",
                "#b5dff3"
            ]
        )

        style_chart_layout(
            fig_pie,
            title_text=f"{selected_value.title()} Contribution",
            show_axes=False
        )

        fig_pie.update_traces(
            textfont=dict(
                color="#e2e2e2",
                size=12
            ),
            marker=dict(
                line=dict(color="#0f172a", width=2)
            )
        )

        st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ANOMALY DETECTION
st.subheader("Anomaly Detection")

mean_value = filtered_df[selected_value].mean()
std_value = filtered_df[selected_value].std()

high_threshold = mean_value + (1.5 * std_value)
low_threshold = mean_value - (1.5 * std_value)

anomalies = filtered_df[
    (filtered_df[selected_value] > high_threshold) |
    (filtered_df[selected_value] < low_threshold)
]

if not anomalies.empty:
    st.warning(f"{len(anomalies)} potential anomalies detected.")

    anomalies_display = anomalies.copy()

    if date_col:
        anomalies_display[date_col] = anomalies_display[date_col].dt.strftime("%Y-%m-%d")

    st.dataframe(
        anomalies_display,
        use_container_width=True
    )

else:
    st.success("No major anomalies detected.")

st.divider()

# BUSINESS INSIGHTS
st.subheader("AI-Style Business Insights")

insights = [
    f"Total {selected_value.lower()} reached {format_number(total_value)} across the selected dataset.",
    f"The average {selected_value.lower()} per record is {format_number(avg_value)}."
]

if category_summary is not None and not category_summary.empty:
    top_category = category_summary.iloc[0][selected_category]
    top_value = category_summary.iloc[0][selected_value]

    bottom_category = category_summary.iloc[-1][selected_category]
    bottom_value = category_summary.iloc[-1][selected_value]

    insights.append(
        f"The top-performing {selected_category.lower()} is {top_category}, generating {format_number(top_value)}."
    )

    insights.append(
        f"The lowest-performing {selected_category.lower()} is {bottom_category}, generating {format_number(bottom_value)}."
    )

if trend_df is not None and len(trend_df) > 1:
    first_value = trend_df[selected_value].iloc[0]
    last_value = trend_df[selected_value].iloc[-1]

    if first_value != 0:
        change_pct = ((last_value - first_value) / first_value) * 100

        if change_pct > 0:
            insights.append(
                f"{selected_value.title()} increased by {change_pct:.2f}% during the selected period."
            )
        elif change_pct < 0:
            insights.append(
                f"{selected_value.title()} decreased by {abs(change_pct):.2f}% during the selected period."
            )
        else:
            insights.append(
                f"{selected_value.title()} remained stable during the selected period."
            )

if not anomalies.empty:
    insights.append(
        "Anomaly records were detected and may require additional business review."
    )
else:
    insights.append(
        "No major anomalies were detected, suggesting stable performance across the selected data."
    )

for insight in insights:
    st.info(insight)

st.divider()

# RECOMMENDATIONS
st.subheader("Recommendations")

st.write("- Focus on high-performing segments to understand what drives strong sales and profitability.")
st.write("- Investigate low-performing categories to identify optimization opportunities.")
st.write("- Review anomaly records for unusual activity, operational risks, or exceptional opportunities.")
st.write("- Use trend analysis to support forecasting and strategic decision-making.")

st.divider()

# DOWNLOAD FILTERED DATA
st.subheader("Download Filtered Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Dataset",
    data=csv,
    file_name="filtered_business_data.csv",
    mime="text/csv"
)

# FOOTER
st.markdown(
    """
    <div style="
        margin-top: 50px;
        padding: 20px;
        text-align: center;
        border-top: 1px solid rgba(45,138,184,0.2);
        color: #9ca3af;
        font-size: 14px;
        background: rgba(15,23,42,0.35);
        border-radius: 12px;
    ">
        Built with ❤️ using Streamlit & Plotly <br>
        <span style="
            color:#2d8ab8;
            font-weight:700;
            font-size:16px;
        ">
            Created by Yahya Sleiman
        </span>
    </div>
    """,
    unsafe_allow_html=True
)
