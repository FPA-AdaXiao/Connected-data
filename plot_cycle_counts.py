import streamlit as st
import pandas as pd
import plotly.express as px

# =================================================
# Page configuration
# =================================================
st.set_page_config(
    page_title="FTT Market Dashboard",
    layout="wide"
)

st.title("📊 FTT Cycle Market Dashboard")

# =================================================
# Load data
# =================================================
@st.cache_data
def load_data():
    df = pd.read_excel(
        "FTT Cycle Data 202511_anonymization.xlsx",
        sheet_name="anonymized_data"
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    return df.dropna(subset=["timestamp"])

df = load_data()

# =================================================
# Sidebar filters (Power BI slicers)
# =================================================
st.sidebar.header("Filters")

machine_list = sorted(df["hb_jiduser"].unique())

selected_machines = st.sidebar.multiselect(
    "Select machines",
    machine_list,
    default=machine_list
)

date_min = df["timestamp"].min().date()
date_max = df["timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(date_min, date_max)
)

start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)

filtered_df = df[
    (df["hb_jiduser"].isin(selected_machines)) &
    (df["timestamp"].between(start_date, end_date))
]

# =================================================
# KPI cards
# =================================================
k1, k2, k3 = st.columns(3)

k1.metric("Total Records", f"{len(filtered_df):,}")
k2.metric("Unique Machines", filtered_df["hb_jiduser"].nunique())

if len(filtered_df):
    k3.metric(
        "Date Span (days)",
        (filtered_df["timestamp"].max() - filtered_df["timestamp"].min()).days
    )
else:
    k3.metric("Date Span (days)", 0)

st.divider()

# =================================================
# Tabs
# =================================================
tab1, tab2, tab3 = st.tabs(
    ["📈 Time Series", "🖥 Machine Analysis", "📊 Data Table"]
)

# -------------------------------------------------
# Time Series
# -------------------------------------------------
with tab1:
    if len(filtered_df) == 0:
        st.warning("No data for selected filters.")
    else:
        ts_df = (
            filtered_df
            .set_index("timestamp")
            .resample("D")
            .size()
            .reset_index(name="records")
        )

        fig = px.line(
            ts_df,
            x="timestamp",
            y="records",
            markers=True
        )

        fig.update_layout(
            hovermode="x unified",
            xaxis_title="NZ Time",
            yaxis_title="Records"
        )

        st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# Machine Analysis
# -------------------------------------------------
with tab2:
    if len(filtered_df) == 0:
        st.warning("No data for selected filters.")
    else:
        machine_df = (
            filtered_df
            .groupby("hb_jiduser")
            .size()
            .reset_index(name="record_count")
            .sort_values("record_count", ascending=False)
        )

        fig = px.bar(
            machine_df,
            x="hb_jiduser",
            y="record_count"
        )

        fig.update_layout(
            xaxis_title="Machine (Anonymized)",
            yaxis_title="Record Count",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# Data Table
# -------------------------------------------------
with tab3:
    st.dataframe(filtered_df, use_container_width=True, height=500)

st.caption("Deployed with Streamlit • Plotly • Python")
