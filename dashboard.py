
import json
import os
from pathlib import Path
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# =====================================================
# BIN2CHAIN - ADMIN & CITIZEN DASHBOARDS
# JSON DEMO MODE
# =====================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORT_FILE = DATA_DIR / "reports.json"
UPLOAD_DIR = BASE_DIR / "uploads"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

STATUS_OPTIONS = ["Submitted", "In Progress", "Resolved"]

DEPARTMENTS = [
    "Road Maintenance Department",
    "Sanitation Department",
    "Water Supply Department",
    "Drainage Department",
    "Electrical Department",
    "Public Safety Department",
    "General Administration",
]

PRIORITIES = ["Low", "Medium", "High", "Critical"]
REVIEW_OPTIONS = ["Pending Review", "Accepted", "Rejected"]


def current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_reports():
    """Read complaint records from JSON."""
    if not REPORT_FILE.exists():
        return []

    try:
        with REPORT_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def save_reports(reports):
    """Save complaint records safely."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    temp_file = REPORT_FILE.with_suffix(".tmp")

    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(
            reports,
            file,
            ensure_ascii=False,
            indent=2,
            default=str
        )

    temp_file.replace(REPORT_FILE)


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
        "resolution_notes": "",
        "review_status": "Pending Review",
        "assigned_department": "",
        "assigned_officer": "",
        "priority": "Medium",
    }

    for column, value in defaults.items():
        if column not in df.columns:
            df[column] = value

        df[column] = df[column].fillna(value)

    return df


def get_photo(photo_path):
    if not photo_path:
        return None

    path = Path(str(photo_path))

    if not path.is_absolute():
        path = BASE_DIR / path

    return path if path.is_file() else None


# =====================================================
# CITIZEN DASHBOARD
# =====================================================

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
    submitted = int((df["status"] == "Submitted").sum())
    in_progress = int((df["status"] == "In Progress").sum())
    resolved = int((df["status"] == "Resolved").sum())

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "कुल रिपोर्ट" if hindi else "Total Reports",
        total
    )

    c2.metric(
        "जमा" if hindi else "Submitted",
        submitted
    )

    c3.metric(
        "प्रगति पर" if hindi else "In Progress",
        in_progress
    )

    c4.metric(
        "समाधान" if hindi else "Resolved",
        resolved
    )

    st.divider()

    st.subheader(
        "📋 सभी शिकायतें"
        if hindi else
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

    st.subheader("Issue Category Analysis")

    st.bar_chart(df["category"].value_counts())


# =====================================================
# ADMIN LOGIN
# =====================================================

def admin_login():

    st.title("🔐 Bin2Chain Admin Login")
    st.caption("Authorized administrators only.")

    with st.form("admin_login_form"):

        username = st.text_input("Admin Username")

        password = st.text_input(
            "Admin Password",
            type="password"
        )

        login_button = st.form_submit_button(
            "Login",
            use_container_width=True
        )

    if login_button:

        configured_password = (
            st.secrets.get("ADMIN_PASSWORD", "")
            if hasattr(st, "secrets") else ""
        ) or os.getenv(
            "ADMIN_PASSWORD",
            "Bin2ChainDemo@2026"
        )

        if (
            username.strip().lower() == "admin"
            and password == configured_password
        ):

            st.session_state.admin_authenticated = True

            st.success("Login successful!")

            st.rerun()

        else:
            st.error("Invalid username or password.")


# =====================================================
# MUNICIPAL ASSIGNMENT
# =====================================================

def save_municipal_assignment(report_id, values):

    reports = load_reports()

    for report in reports:

        if str(report.get("report_id")) == str(report_id):

            report.update(values)

            report.setdefault(
                "assignment_history", []
            ).append({

                "assigned_department":
                    values.get("assigned_department", ""),

                "assigned_officer":
                    values.get("assigned_officer", ""),

                "priority":
                    values.get("priority", "Medium"),

                "assignment_remarks":
                    values.get("assignment_remarks", ""),

                "review_status":
                    values.get("review_status", "Pending Review"),

                "timestamp": current_timestamp(),

            })

            save_reports(reports)

            return True, None

    return False, "Complaint not found."


def save_complaint_status(
    report_id,
    old_status,
    new_status,
    admin_remarks,
    resolution_notes
):

    reports = load_reports()

    for report in reports:

        if str(report.get("report_id")) == str(report_id):

            report["status"] = new_status

            report["admin_remarks"] = admin_remarks

            report["resolution_notes"] = resolution_notes

            report.setdefault(
                "status_history", []
            ).append({

                "status": new_status,

                "remarks": admin_remarks or resolution_notes,

                "timestamp": current_timestamp(),

                "changed_by": "admin",

            })

            save_reports(reports)

            return True, None

    return False, "Complaint not found."


def render_department_assignment(reports):

    st.divider()

    st.header("🏛️ Municipal Complaint Management")

    st.caption(
        "Verify citizen complaints, assign departments "
        "and officers, and manage priority."
    )

    valid_reports = [
        r for r in reports if r.get("report_id")
    ]

    if not valid_reports:
        st.info("No complaints available.")
        return

    report_ids = [
        str(r["report_id"]) for r in valid_reports
    ]

    selected_id = st.selectbox(
        "Select Complaint for Municipal Review",
        report_ids,
        key="municipal_assignment_report"
    )

    report = next(
        (
            r for r in valid_reports
            if str(r["report_id"]) == selected_id
        ),
        None
    )

    if report is None:
        return

    st.markdown("### 📄 Complaint Details")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**Report ID:**", selected_id)

        st.write(
            "**Category:**",
            report.get("category") or "N/A"
        )

        st.write(
            "**Location:**",
            report.get("location") or "N/A"
        )

    with col2:

        st.write(
            "**Citizen Status:**",
            report.get("status") or "Submitted"
        )

        st.write(
            "**Created At:**",
            report.get("created_at") or "N/A"
        )

        st.write(
            "**Priority:**",
            report.get("priority") or "Medium"
        )

    st.write(
        "**Description:**",
        report.get("description") or "N/A"
    )

    photo_file = get_photo(report.get("photo"))

    if photo_file:

        with st.expander("View Citizen Uploaded Photo"):

            st.image(
                str(photo_file),
                caption="Citizen Uploaded Photo",
                use_container_width=True
            )

    current_review = (
        report.get("review_status")
        or "Pending Review"
    )

    if current_review not in REVIEW_OPTIONS:
        current_review = "Pending Review"

    department_options = ["Not Assigned"] + DEPARTMENTS

    current_department = (
        report.get("assigned_department")
        or "Not Assigned"
    )

    if current_department not in department_options:
        department_options.append(current_department)

    current_priority = report.get("priority") or "Medium"

    if current_priority not in PRIORITIES:
        current_priority = "Medium"

    st.markdown(
        "### 🏛️ Verification and Department Assignment"
    )

    with st.form("municipal_assignment_form"):

        review_status = st.selectbox(
            "Verification Decision",
            REVIEW_OPTIONS,
            index=REVIEW_OPTIONS.index(current_review)
        )

        department = st.selectbox(
            "Assign Municipal Department",
            department_options,
            index=department_options.index(current_department)
        )

        officer = st.text_input(
            "Responsible Officer Name",
            value=report.get("assigned_officer") or ""
        )

        priority = st.selectbox(
            "Complaint Priority",
            PRIORITIES,
            index=PRIORITIES.index(current_priority)
        )

        rejection_reason = st.text_area(
            "Rejection Reason",
            value=report.get("rejection_reason") or ""
        )

        remarks = st.text_area(
            "Assignment Remarks",
            value=report.get("assignment_remarks") or ""
        )

        save_assignment = st.form_submit_button(
            "💾 Save Municipal Assignment",
            use_container_width=True
        )

    if save_assignment:

        if (
            review_status == "Rejected"
            and not rejection_reason.strip()
        ):

            st.error("Please enter a rejection reason.")

        elif (
            review_status == "Accepted"
            and department == "Not Assigned"
        ):

            st.error("Please select a municipal department.")

        elif (
            review_status == "Accepted"
            and not officer.strip()
        ):

            st.error("Please enter the responsible officer's name.")

        else:

            values = {

                "review_status": review_status,

                "assigned_department":
                    "" if department == "Not Assigned"
                    else department,

                "assigned_officer": officer.strip(),

                "priority": priority,

                "rejection_reason": rejection_reason.strip(),

                "assignment_remarks": remarks.strip(),

            }

            changed = any(
                (report.get(key) or "") != value
                for key, value in values.items()
            )

            if not changed:

                st.info("No assignment changes detected.")

            else:

                success, error = save_municipal_assignment(
                    selected_id,
                    values
                )

                if success:

                    st.success(
                        f"Municipal assignment saved for {selected_id}."
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Unable to save assignment: {error}"
                    )

    st.divider()

    st.subheader("📋 Current Assignment Summary")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Verification",
        report.get("review_status") or "Pending Review"
    )

    c2.metric(
        "Priority",
        report.get("priority") or "Medium"
    )

    c3.metric(
        "Department",
        report.get("assigned_department") or "Not Assigned"
    )

    c4.metric(
        "Officer",
        report.get("assigned_officer") or "Not Assigned"
    )

    if report.get("review_status") == "Rejected":

        st.warning(
            "Rejection Reason: "
            + (report.get("rejection_reason") or "Not recorded")
        )

    st.subheader("🕒 Municipal Assignment History")

    history = report.get("assignment_history", [])

    if history:

        st.dataframe(
            pd.DataFrame(history),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No assignment history recorded yet.")


# =====================================================
# ADMIN DASHBOARD
# =====================================================

def render_admin_dashboard():

    st.title("🛡️ Bin2Chain Admin Panel")

    st.caption("Manage and monitor citizen complaints.")

    reports = load_reports()

    if not reports:

        st.info("No citizen complaints available.")
        return

    df = create_reports_dataframe(reports)

    total = len(df)

    submitted = int(
        (df["status"] == "Submitted").sum()
    )

    in_progress = int(
        (df["status"] == "In Progress").sum()
    )

    resolved = int(
        (df["status"] == "Resolved").sum()
    )

    st.subheader("📊 Complaint Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Reports", total)

    c2.metric("Submitted", submitted)

    c3.metric("In Progress", in_progress)

    c4.metric("Resolved", resolved)

    st.divider()

    st.subheader("🔎 Search and Filter Reports")

    search_text = st.text_input(
        "Search by Report ID, Location or Description",
        key="admin_search"
    )

    category_options = (
        ["All"]
        + sorted(df["category"].astype(str).unique().tolist())
    )

    status_options = ["All"] + STATUS_OPTIONS

    c1, c2 = st.columns(2)

    with c1:

        selected_category = st.selectbox(
            "Filter by Category",
            category_options
        )

    with c2:

        selected_status = st.selectbox(
            "Filter by Status",
            status_options
        )

    filtered_df = df.copy()

    if search_text.strip():

        mask = filtered_df[
            ["report_id", "location", "description"]
        ].astype(str).apply(

            lambda col: col.str.contains(
                search_text.strip(),
                case=False,
                regex=False,
                na=False
            )

        ).any(axis=1)

        filtered_df = filtered_df[mask]

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

    st.subheader("📋 All Citizen Complaints")

    st.dataframe(
        filtered_df[
            [
                "report_id",
                "category",
                "location",
                "description",
                "status",
                "created_at"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    render_department_assignment(reports)

    st.divider()

    st.subheader("📥 Download Reports")

    export_df = filtered_df.copy()

    csv_data = export_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    c1, c2 = st.columns(2)

    with c1:

        st.download_button(
            "⬇️ Download CSV",
            data=csv_data,
            file_name="Bin2Chain_Complaints.csv",
            mime="text/csv",
            use_container_width=True
        )

    with c2:

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
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )

        except ImportError:

            st.warning(
                "Excel export requires openpyxl. "
                "Install using: pip install openpyxl"
            )

    st.divider()

    st.subheader("✏️ Manage Complaint Status")

    report_ids = [
        str(r["report_id"])
        for r in reports
        if r.get("report_id")
    ]

    if not report_ids:

        st.warning("No valid Report IDs found.")
        return

    selected_id = st.selectbox(
        "Select Report ID",
        report_ids,
        key="selected_admin_report"
    )

    selected_report = next(
        (
            r for r in reports
            if str(r["report_id"]) == selected_id
        ),
        None
    )

    if selected_report is None:
        return

    st.markdown("### 📄 Complaint Details")

    st.write(
        "**Category:**",
        selected_report.get("category") or "N/A"
    )

    st.write(
        "**Location:**",
        selected_report.get("location") or "N/A"
    )

    st.write(
        "**Description:**",
        selected_report.get("description") or "N/A"
    )

    st.write(
        "**Current Status:**",
        selected_report.get("status") or "Submitted"
    )

    st.write(
        "**Created At:**",
        selected_report.get("created_at") or "N/A"
    )

    photo_file = get_photo(
        selected_report.get("photo")
    )

    if photo_file:

        st.image(
            str(photo_file),
            caption="Citizen Uploaded Photo",
            use_container_width=True
        )

    st.divider()

    st.markdown("### 📝 Update Complaint")

    current_status = (
        selected_report.get("status")
        or "Submitted"
    )

    if current_status not in STATUS_OPTIONS:
        current_status = "Submitted"

    with st.form("update_status_form"):

        new_status = st.selectbox(
            "Update Complaint Status",
            STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(current_status)
        )

        admin_remarks = st.text_area(
            "Admin Remarks",
            value=selected_report.get("admin_remarks") or "",
            placeholder="Enter an update for this complaint..."
        )

        resolution_notes = st.text_area(
            "Resolution Notes",
            value=selected_report.get("resolution_notes") or "",
            placeholder="Describe the action taken to resolve the issue..."
        )

        update_button = st.form_submit_button(
            "💾 Update Complaint",
            use_container_width=True
        )

    if update_button:

        if (
            new_status == "Resolved"
            and not resolution_notes.strip()
        ):

            st.error(
                "Please enter Resolution Notes before "
                "marking a complaint as Resolved."
            )

        else:

            old_status = (
                selected_report.get("status")
                or "Submitted"
            )

            changed = (

                old_status != new_status

                or (
                    selected_report.get("admin_remarks") or ""
                ) != admin_remarks.strip()

                or (
                    selected_report.get("resolution_notes") or ""
                ) != resolution_notes.strip()

            )

            if not changed:

                st.info("No changes detected.")

            else:

                success, error = save_complaint_status(
                    selected_id,
                    old_status,
                    new_status,
                    admin_remarks.strip(),
                    resolution_notes.strip()
                )

                if success:

                    st.success(
                        f"Report {selected_id} updated successfully!"
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Unable to update complaint: {error}"
                    )

    st.divider()

    st.subheader("🕒 Complaint History")

    history = selected_report.get("status_history", [])

    if history:

        st.dataframe(
            pd.DataFrame(history),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No status history available yet. "
            "History will be recorded after the first admin update."
        )

    st.divider()

    st.subheader("📈 Complaint Category Analysis")

    category_counts = df["category"].value_counts()

    if not category_counts.empty:

        st.bar_chart(category_counts)

    st.subheader("📊 Status Analysis")

    st.bar_chart(
        df["status"].value_counts().reindex(
            STATUS_OPTIONS,
            fill_value=0
        )
    )

    st.divider()

    st.subheader("📌 Admin Summary")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Resolution Rate",
            f"{(resolved / total * 100) if total else 0:.1f}%"
        )

    with c2:

        st.metric(
            "Open Complaints",
            submitted + in_progress
        )


# =====================================================
# POWER BI EMBEDDED DASHBOARD
# =====================================================

def render_powerbi_dashboard():

    st.divider()

    st.title("📊 Bin2Chain Analytics Dashboard")

    st.caption(
        "Advanced analytics and reporting"
    )

    powerbi_url = (
        "https://app.powerbi.com/view?r=eyJrIjoiM2M0NGQ5NmItMDVhMy00YjIzLWFhMWItNjEyZDIzNjRjMjk5IiwidCI6ImFhODc0Zjc3LThkYmQtNDk1OC04NmVkLWViNWNjMzFmMzQ0NiJ9"
    )

    components.iframe(
        powerbi_url,
        width=None,
        height=700,
        scrolling=True
    )


# =====================================================
# ADMIN PANEL ENTRY POINT
# =====================================================

def render_admin_panel():

    if not st.session_state.get(
        "admin_authenticated",
        False
    ):

        admin_login()
        return

    c1, c2 = st.columns([4, 1])

    with c1:

        st.title("🌱 Bin2Chain Administration")

    with c2:

        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.admin_authenticated = False

            st.rerun()

    st.divider()

    render_admin_dashboard()

    # Power BI report appears below complaint management
    render_powerbi_dashboard()
