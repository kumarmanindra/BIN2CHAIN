
import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from io import BytesIO

# ==========================================
# Bin2Chain ADMIN DASHBOARD
# ==========================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORT_FILE = DATA_DIR / "reports.json"

DATA_DIR.mkdir(exist_ok=True)

# Local development password only.
# Change this before public deployment.
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

STATUS_OPTIONS = [
    "Submitted",
    "In Progress",
    "Resolved"
]


# ==========================================
# DATE AND TIME
# ==========================================

def current_timestamp():
    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


# ==========================================
# LOAD REPORTS
# ==========================================

def load_reports():

    if not REPORT_FILE.exists():
        return []

    try:
        with open(
            REPORT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data, list):
            return []

        # Ensure older reports have the new fields.
        for report in data:

            if not isinstance(report, dict):
                continue

            report.setdefault("status", "Submitted")
            report.setdefault("admin_remarks", "")
            report.setdefault("resolution_notes", "")
            report.setdefault("status_history", [])

            if not isinstance(
                report["status_history"], list
            ):
                report["status_history"] = []

        return [
            report for report in data
            if isinstance(report, dict)
        ]

    except (json.JSONDecodeError, OSError):
        return []


# ==========================================
# SAVE REPORTS
# ==========================================

def save_reports(reports):

    DATA_DIR.mkdir(exist_ok=True)

    temp_file = REPORT_FILE.with_suffix(".tmp")

    temp_file.write_text(
        json.dumps(
            reports,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    temp_file.replace(REPORT_FILE)


# ==========================================
# DATAFRAME HELPER
# ==========================================

def create_reports_dataframe(reports):

    if not reports:
        return pd.DataFrame()

    df = pd.DataFrame(reports)

    defaults = {
        "report_id": "",
        "category": "Other",
        "location": "",
        "description": "",
        "status": "Submitted",
        "created_at": "",
        "admin_remarks": "",
        "resolution_notes": ""
    }

    for column, default_value in defaults.items():

        if column not in df.columns:
            df[column] = default_value

        df[column] = df[column].fillna(default_value)

    return df


# ==========================================
# CITIZEN DASHBOARD
# ==========================================

def render_dashboard(language="English"):

    hindi = language == "Hindi"

    st.title(
        "📊 नागरिक डैशबोर्ड"
        if hindi else
        "📊 Citizen Dashboard"
    )

    reports = load_reports()

    if not reports:

        st.info(
            "अभी कोई रिपोर्ट नहीं है।"
            if hindi else
            "No reports submitted yet."
        )

        return

    df = create_reports_dataframe(reports)

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

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "कुल रिपोर्ट" if hindi else "Total Reports",
        total
    )

    col2.metric(
        "लंबित" if hindi else "Submitted",
        int(submitted)
    )

    col3.metric(
        "प्रगति में" if hindi else "In Progress",
        int(in_progress)
    )

    col4.metric(
        "हल की गई" if hindi else "Resolved",
        int(resolved)
    )

    st.divider()

    st.subheader(
        "📋 सभी रिपोर्ट" if hindi else
        "📋 All Reports"
    )

    display_columns = [
        "report_id",
        "category",
        "location",
        "status",
        "created_at"
    ]

    st.dataframe(
        df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    if "category" in df.columns:

        st.subheader("Issue Category Analysis")

        st.bar_chart(
            df["category"].value_counts()
        )


# ==========================================
# ADMIN LOGIN
# ==========================================

def admin_login():

    st.title("🔐 Bin2Chain Admin Login")

    st.caption(
        "Authorized administrators only."
    )

    with st.form("admin_login_form"):

        username = st.text_input(
            "Admin Username"
        )

        password = st.text_input(
            "Admin Password",
            type="password"
        )

        login_button = st.form_submit_button(
            "Login",
            use_container_width=True
        )

        if login_button:

            if (
                username.strip().lower() == "admin"
                and password == ADMIN_PASSWORD
            ):

                st.session_state.admin_authenticated = True

                st.success("Login successful!")

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )


# ==========================================
# ADMIN DASHBOARD
# ==========================================

def render_admin_dashboard():

    st.title("🛡️ Bin2Chain Admin Panel")

    st.caption(
        "Manage and monitor citizen complaints."
    )

    reports = load_reports()

    if not reports:

        st.info(
            "No citizen complaints available."
        )

        return

    df = create_reports_dataframe(reports)

    # ======================================
    # COMPLAINT OVERVIEW
    # ======================================

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

    st.subheader("📊 Complaint Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Reports", total)

    col2.metric("Submitted", int(submitted))

    col3.metric("In Progress", int(in_progress))

    col4.metric("Resolved", int(resolved))

    st.divider()

    # ======================================
    # SEARCH AND FILTER
    # ======================================

    st.subheader("🔎 Search and Filter Reports")

    search_text = st.text_input(
        "Search by Report ID, Location or Description",
        key="admin_search"
    )

    category_options = (
        ["All"] +
        sorted(df["category"].astype(str).unique().tolist())
    )

    status_options = ["All"] + STATUS_OPTIONS

    col1, col2 = st.columns(2)

    with col1:

        selected_category = st.selectbox(
            "Filter by Category",
            category_options
        )

    with col2:

        selected_status = st.selectbox(
            "Filter by Status",
            status_options
        )

    filtered_df = df.copy()

    if search_text.strip():

        searchable_columns = [
            "report_id",
            "location",
            "description"
        ]

        search_mask = (
            filtered_df[searchable_columns]
            .astype(str)
            .apply(
                lambda column: column.str.contains(
                    search_text.strip(),
                    case=False,
                    regex=False,
                    na=False
                )
            )
            .any(axis=1)
        )

        filtered_df = filtered_df[search_mask]

    if selected_category != "All":

        filtered_df = filtered_df[
            filtered_df["category"] == selected_category
        ]

    if selected_status != "All":

        filtered_df = filtered_df[
            filtered_df["status"] == selected_status
        ]

    st.write(
        f"Showing {len(filtered_df)} of {total} reports"
    )

    # ======================================
    # ALL CITIZEN COMPLAINTS
    # ======================================

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
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ======================================
    # EXPORT REPORTS
    # ======================================

    st.subheader("📥 Download Reports")

    export_df = filtered_df.copy()

    csv_data = export_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "⬇️ Download CSV",
            data=csv_data,
            file_name="Bin2Chain_Complaints.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:

        try:

            excel_buffer = BytesIO()

            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:

                export_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Complaints"
                )

            st.download_button(
                "⬇️ Download Excel",
                data=excel_buffer.getvalue(),
                file_name="Bin2Chain_Complaints.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        except ImportError:

            st.warning(
                "Excel export requires openpyxl. "
                "Install it using: pip install openpyxl"
            )

    st.divider()

    # ======================================
    # MANAGE COMPLAINT STATUS
    # ======================================

    st.subheader("✏️ Manage Complaint Status")

    report_ids = [
        str(report.get("report_id"))
        for report in reports
        if report.get("report_id")
    ]

    if not report_ids:

        st.warning("No valid Report IDs found.")

        return

    selected_report_id = st.selectbox(
        "Select Report ID",
        report_ids,
        key="selected_admin_report"
    )

    selected_report = next(
        (
            report for report in reports
            if str(report.get("report_id"))
            == selected_report_id
        ),
        None
    )

    if selected_report is None:
        return

    # ======================================
    # COMPLAINT DETAILS
    # ======================================

    st.markdown("### 📄 Complaint Details")

    st.write(
        "**Category:**",
        selected_report.get("category", "N/A")
    )

    st.write(
        "**Location:**",
        selected_report.get("location", "N/A")
    )

    st.write(
        "**Description:**",
        selected_report.get("description", "N/A")
    )

    st.write(
        "**Current Status:**",
        selected_report.get("status", "Submitted")
    )

    st.write(
        "**Created At:**",
        selected_report.get("created_at", "N/A")
    )

    # ======================================
    # CITIZEN UPLOADED PHOTO
    # ======================================

    photo_path = selected_report.get("photo")

    if photo_path:

        photo_file = Path(photo_path)

        if not photo_file.is_absolute():
            photo_file = BASE_DIR / photo_file

        if photo_file.is_file():

            st.image(
                str(photo_file),
                caption="Citizen Uploaded Photo",
                use_container_width=True
            )

    st.divider()

    # ======================================
    # UPDATE STATUS AND ADMIN REMARKS
    # ======================================

    st.markdown("### 📝 Update Complaint")

    current_status = selected_report.get(
        "status", "Submitted"
    )

    if current_status not in STATUS_OPTIONS:
        current_status = "Submitted"

    with st.form(
        "update_status_form",
        clear_on_submit=False
    ):

        new_status = st.selectbox(
            "Update Complaint Status",
            STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(current_status)
        )

        admin_remarks = st.text_area(
            "Admin Remarks",
            value=selected_report.get(
                "admin_remarks", ""
            ),
            placeholder="Enter an update for this complaint..."
        )

        resolution_notes = st.text_area(
            "Resolution Notes",
            value=selected_report.get(
                "resolution_notes", ""
            ),
            placeholder="Describe the action taken to resolve the issue..."
        )

        update_button = st.form_submit_button(
            "💾 Update Complaint",
            use_container_width=True
        )

        if update_button:

            old_status = selected_report.get(
                "status", "Submitted"
            )

            old_remarks = selected_report.get(
                "admin_remarks", ""
            )

            old_resolution = selected_report.get(
                "resolution_notes", ""
            )

            if (
                new_status == "Resolved"
                and not resolution_notes.strip()
            ):

                st.error(
                    "Please enter Resolution Notes before marking a complaint as Resolved."
                )

            else:

                changes = []

                if old_status != new_status:
                    changes.append(
                        f"Status changed from {old_status} to {new_status}"
                    )

                if old_remarks != admin_remarks:
                    changes.append("Admin remarks updated")

                if old_resolution != resolution_notes:
                    changes.append("Resolution notes updated")

                if changes:

                    selected_report["status"] = new_status

                    selected_report["admin_remarks"] = (
                        admin_remarks.strip()
                    )

                    selected_report["resolution_notes"] = (
                        resolution_notes.strip()
                    )

                    history = selected_report.get(
                        "status_history", []
                    )

                    if not isinstance(history, list):
                        history = []

                    history.append({
                        "timestamp": current_timestamp(),
                        "status": new_status,
                        "remarks": admin_remarks.strip(),
                        "changes": changes
                    })

                    selected_report["status_history"] = history

                    save_reports(reports)

                    st.success(
                        f"Report {selected_report_id} updated successfully!"
                    )

                    st.rerun()

                else:

                    st.info(
                        "No changes detected."
                    )

    st.divider()

    # ======================================
    # COMPLAINT HISTORY
    # ======================================

    st.subheader("🕒 Complaint History")

    history = selected_report.get(
        "status_history", []
    )

    if history:

        history_df = pd.DataFrame(history)

        history_columns = [
            col for col in [
                "timestamp",
                "status",
                "remarks",
                "changes"
            ]
            if col in history_df.columns
        ]

        st.dataframe(
            history_df[history_columns],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No status history available yet. "
            "History will be recorded after the first admin update."
        )

    st.divider()

    # ======================================
    # CATEGORY ANALYSIS
    # ======================================

    st.subheader("📈 Complaint Category Analysis")

    category_counts = df["category"].value_counts()

    if not category_counts.empty:

        st.bar_chart(category_counts)

    # ======================================
    # STATUS ANALYSIS
    # ======================================

    st.subheader("📊 Status Analysis")

    status_counts = (
        df["status"]
        .value_counts()
        .reindex(STATUS_OPTIONS, fill_value=0)
    )

    st.bar_chart(status_counts)

    # ======================================
    # ADMIN SUMMARY
    # ======================================

    st.divider()

    st.subheader("📌 Admin Summary")

    col1, col2 = st.columns(2)

    with col1:

        resolution_rate = (
            (resolved / total) * 100
            if total else 0
        )

        st.metric(
            "Resolution Rate",
            f"{resolution_rate:.1f}%"
        )

    with col2:

        pending_reports = submitted + in_progress

        st.metric(
            "Open Complaints",
            int(pending_reports)
        )


# ==========================================
# ADMIN PANEL ENTRY POINT
# ==========================================

def render_admin_panel():

    if not st.session_state.get(
        "admin_authenticated", False
    ):

        admin_login()

        return

    col1, col2 = st.columns([4, 1])

    with col1:

        st.title("🌱 Bin2Chain Administration")

    with col2:

        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.admin_authenticated = False

            st.rerun()

    st.divider()

    render_admin_dashboard()
