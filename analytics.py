
import streamlit as st
import pandas as pd
import json
from pathlib import Path

# =====================================
# NAGRIQ ADMIN ANALYTICS
# =====================================

BASE_DIR = Path(__file__).resolve().parent
REPORT_FILE = BASE_DIR / "data" / "reports.json"


# =====================================
# LOAD COMPLAINT DATA
# =====================================

def load_reports():

    if not REPORT_FILE.exists():
        return pd.DataFrame()

    try:
        with open(REPORT_FILE, "r", encoding="utf-8") as file:
            reports = json.load(file)

        if not isinstance(reports, list):
            return pd.DataFrame()

        if not reports:
            return pd.DataFrame()

        df = pd.DataFrame(reports)

        required_columns = [
            "report_id",
            "category",
            "location",
            "description",
            "status",
            "created_at"
        ]

        for column in required_columns:
            if column not in df.columns:
                df[column] = "Unknown"

        df["status"] = (
            df["status"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .str.title()
        )

        return df

    except (OSError, json.JSONDecodeError) as error:
        st.error(f"Error loading reports: {error}")
        return pd.DataFrame()


# =====================================
# ADMIN ANALYTICS DASHBOARD
# =====================================

def render_admin_analytics():

    st.title("📊 NAGRIQ Admin Analytics")

    st.caption(
        "Monitor citizen complaints and "
        "municipal service performance."
    )

    st.divider()

    df = load_reports()

    if df.empty:
        st.info("No complaints available yet.")
        return

    # =================================
    # COMPLAINT OVERVIEW
    # =================================

    st.subheader("📌 Complaint Overview")

    total = len(df)

    submitted = (
        df["status"] == "Submitted"
    ).sum()

    in_progress = (
        df["status"] == "In Progress"
    ).sum()

    resolved = (
        df["status"] == "Resolved"
    ).sum()

    resolution_rate = (
        resolved / total * 100
        if total > 0 else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Complaints", total)

    col2.metric("Submitted", int(submitted))

    col3.metric("In Progress", int(in_progress))

    col4.metric("Resolved", int(resolved))

    st.metric(
        "Resolution Rate",
        f"{resolution_rate:.1f}%"
    )

   
    # =================================
    # COMPLAINT CATEGORY ANALYSIS
    # =================================

    st.divider()

    st.subheader("📊 Complaint Category Analysis")

    category_counts = (
        df["category"]
        .value_counts()
        .reset_index()
    )

    category_counts.columns = [
        "Category",
        "Complaints"
    ]

    col1, col2 = st.columns(2)

    with col1:

        st.bar_chart(
            category_counts.set_index("Category")
        )

    with col2:

        st.dataframe(
            category_counts,
            use_container_width=True,
            hide_index=True
        )

    # =================================
    # COMPLAINT STATUS ANALYSIS
    # =================================

    st.divider()

    st.subheader("📈 Complaint Status Analysis")

    status_counts = (
        df["status"]
        .value_counts()
        .reset_index()
    )

    status_counts.columns = [
        "Status",
        "Complaints"
    ]

    col1, col2 = st.columns(2)

    with col1:

        st.bar_chart(
            status_counts.set_index("Status")
        )

    with col2:

        st.dataframe(
            status_counts,
            use_container_width=True,
            hide_index=True
        )


    # =================================
    # MONTHLY COMPLAINT TRENDS
    # =================================

    st.divider()

    st.subheader("📅 Monthly Complaint Trends")

    # Convert created_at into datetime
    trend_df = df.copy()

    trend_df["created_at"] = pd.to_datetime(
        trend_df["created_at"],
        errors="coerce",
        utc=True
    )

    trend_df = trend_df.dropna(
        subset=["created_at"]
    )

    if not trend_df.empty:

        # Convert timezone to local display time
        trend_df["created_at"] = (
            trend_df["created_at"]
            .dt.tz_convert("Asia/Kolkata")
        )

        # Monthly analysis
        trend_df["Month"] = (
            trend_df["created_at"]
            .dt.strftime("%Y-%m")
        )

        monthly_data = (
            trend_df.groupby("Month")
            .size()
            .reset_index(name="Complaints")
            .sort_values("Month")
        )

        st.write("**Monthly Complaint Volume**")

        st.line_chart(
            monthly_data.set_index("Month")
        )

        # Daily analysis
        trend_df["Date"] = (
            trend_df["created_at"]
            .dt.strftime("%Y-%m-%d")
        )

        daily_data = (
            trend_df.groupby("Date")
            .size()
            .reset_index(name="Complaints")
            .sort_values("Date")
        )

        st.write("**Daily Complaint Volume**")

        st.bar_chart(
            daily_data.set_index("Date")
        )

        # Summary
        col1, col2 = st.columns(2)

        col1.metric(
            "Total Days Recorded",
            trend_df["Date"].nunique()
        )

        col2.metric(
            "Months Recorded",
            trend_df["Month"].nunique()
        )

    else:

        st.info("No valid complaint dates available.")

    # =================================
    # ALL COMPLAINTS
    # =================================

    st.subheader("📋 All Citizen Complaints")

    display_columns = [
        "report_id",
        "category",
        "location",
        "description",
        "status",
        "created_at"
    ]

    st.dataframe(
        df[display_columns],
        use_container_width=True,
        hide_index=True
    )


# =====================================
# RUN AS STANDALONE STREAMLIT APP
# =====================================

if __name__ == "__main__":
    render_admin_analytics()
