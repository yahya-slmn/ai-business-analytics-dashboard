import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="AI Business Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>

    /* Main App Background */
    .stApp {
        background: linear-gradient(
            135deg,
            #050816 0%,
            #081120 40%,
            #0b1d35 100%
        );
        color: #e2e2e2;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #111827 0%,
            #0f172a 100%
        );
        border-right: 1px solid rgba(45,138,184,0.25);
    }

    /* Sidebar Header */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label {
        color: #e2e2e2 !important;
    }

    /* KPI Cards */
    div[data-testid="metric-container"] {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(45,138,184,0.25);
        padding: 18px;
        border-radius: 18px;
        box-shadow: 0 0 20px rgba(45,138,184,0.08);
    }

    /* Select Boxes */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #0f172a;
        border-radius: 12px;
    }

    /* Multiselect */
    .stMultiSelect div[data-baseweb="select"] {
        background-color: #0f172a;
        border-radius: 12px;
    }

    /* Date Input */
    .stDateInput {
        background-color: #0f172a;
        border-radius: 12px;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 14px;
        overflow: hidden;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(
            135deg,
            #2d8ab8,
            #1f6f96
        );
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
    }

    .stButton button:hover {
        background: linear-gradient(
            135deg,
            #3ca3d6,
            #2d8ab8
        );
        color: white;
    }

    /* Download Button */
    .stDownloadButton button {
        background: linear-gradient(
            135deg,
            #2d8ab8,
            #1f6f96
        );
        color: white;
        border-radius: 12px;
        border: none;
    }

    /* Section Titles */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Horizontal Divider */
    hr {
        border-color: rgba(226,226,226,0.1);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("AI-Powered Business Analytics Dashboard")
st.write(
    "Analyze sales and profit performance with interactive KPIs, trends, category analysis, and business insights."
)

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if "df" not in st.session_state:
    st.session_state.df = None

if st.button("Use Sample Business Dataset"):
    st.session_state.df = pd.read_csv("sample_data/business_sales_dataset.csv")

if uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = st.session_state.df

if df is None:
    st.info("Upload a CSV file or use the sample dataset to begin analysis.")
    st.stop()

# --------------------------------------------------
# DATA PREPARATION
# --------------------------------------------------
# --------------------------------------------------
# NUMBER FORMATTER
# --------------------------------------------------

def format_number(value):

    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"

    elif abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"

    elif abs(value) >= 1_000:
        return f"${value / 1_000:.2f}K"

    else:
        return f"${value:,.0f}"
# Detect date column

date_cols = [col for col in df.columns if "date" in col.lower()]

if date_cols:
    date_col = date_cols[0]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
else:
    date_col = None

# Detect numeric columns

numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

# Keep only Sales & Profit KPIs if available

priority_metrics = []

for col in numeric_cols:
    if col.lower() in ["sales", "profit"]:
        priority_metrics.append(col)

kpi_options = priority_metrics if priority_metrics else numeric_cols

# Detect categorical columns

categorical_cols = [
    col for col in df.select_dtypes(include=["object"]).columns.tolist()
    if col not in date_cols
]

if not numeric_cols:
    st.error("No numeric columns found in the uploaded dataset.")
    st.stop()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Dashboard Controls")

selected_value = st.sidebar.selectbox(
    "Select KPI",
    kpi_options
)

filtered_df = df.copy()

# --------------------------------------------------
# DATE FILTER
# --------------------------------------------------

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

# --------------------------------------------------
# CATEGORY FILTER
# --------------------------------------------------

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

# --------------------------------------------------
# FORMAT DISPLAY DATAFRAME
# --------------------------------------------------

display_df = filtered_df.copy()

if date_col:
    display_df[date_col] = display_df[date_col].dt.strftime("%Y-%m-%d")

# --------------------------------------------------
# KPI OVERVIEW
# --------------------------------------------------

st.subheader("Executive KPI Overview")

# KPI calculations

total_value = filtered_df[selected_value].sum()
avg_value = filtered_df[selected_value].mean()
max_value = filtered_df[selected_value].max()
records_count = filtered_df.shape[0]

# Profit Margin

profit_margin = None

sales_col = next((c for c in numeric_cols if c.lower() == "sales"), None)
profit_col = next((c for c in numeric_cols if c.lower() == "profit"), None)

if sales_col and profit_col:
    sales_total = filtered_df[sales_col].sum()
    profit_total = filtered_df[profit_col].sum()

    if sales_total != 0:
        profit_margin = (profit_total / sales_total) * 100

# KPI Layout

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

# --------------------------------------------------
# DATASET PREVIEW
# --------------------------------------------------

st.subheader("Dataset Preview")

st.dataframe(
    display_df.head(10),
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# TREND ANALYSIS
# --------------------------------------------------

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
    fig_trend.update_layout(
            height=500,
            plot_bgcolor="rgba(15,23,42,0.75)",
            paper_bgcolor="rgba(15,23,42,0.75)",
            font_color="#e2e2e2",
            title_font_size=22,
            xaxis_title="Month",
            yaxis_title=selected_value.title(),
            hovermode="x unified"
        )

    st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# --------------------------------------------------
# CATEGORY PERFORMANCE ANALYSIS
# --------------------------------------------------

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
        opacity=0.9
        )

        fig_bar.update_layout(
                height=500,
                plot_bgcolor="rgba(15,23,42,0.75)",
                paper_bgcolor="rgba(15,23,42,0.75)",
                font_color="#e2e2e2",
                title_font_size=22
            )

        fig_bar.update_layout(height=500)

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

        fig_pie.update_layout(
                height=500,
                plot_bgcolor="rgba(15,23,42,0.75)",
                paper_bgcolor="rgba(15,23,42,0.75)",
                font_color="#e2e2e2",
                title_font_size=22
            )

        st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# --------------------------------------------------
# ANOMALY DETECTION
# --------------------------------------------------

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

# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

st.subheader("AI-Style Business Insights")

insights = [
    f"Total {selected_value.lower()} reached ${total_value:,.0f} across the selected dataset.",
    f"The average {selected_value.lower()} per record is ${avg_value:,.0f}."
]

if category_summary is not None and not category_summary.empty:

    top_category = category_summary.iloc[0][selected_category]
    top_value = category_summary.iloc[0][selected_value]

    bottom_category = category_summary.iloc[-1][selected_category]
    bottom_value = category_summary.iloc[-1][selected_value]

    insights.append(
        f"The top-performing {selected_category.lower()} is {top_category}, generating ${top_value:,.0f}."
    )

    insights.append(
        f"The lowest-performing {selected_category.lower()} is {bottom_category}, generating ${bottom_value:,.0f}."
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

for insight in insights:
    st.info(insight)

st.divider()

# --------------------------------------------------
# RECOMMENDATIONS
# --------------------------------------------------

st.subheader("Recommendations")

st.write("- Focus on high-performing segments to understand what drives strong sales and profitability.")
st.write("- Investigate low-performing categories to identify optimization opportunities.")
st.write("- Review anomaly records for unusual activity, operational risks, or exceptional opportunities.")
st.write("- Use trend analysis to support forecasting and strategic decision-making.")

st.divider()

# --------------------------------------------------
# DOWNLOAD FILTERED DATA
# --------------------------------------------------

st.subheader("Download Filtered Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Dataset",
    data=csv,
    file_name="filtered_business_data.csv",
    mime="text/csv"
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

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