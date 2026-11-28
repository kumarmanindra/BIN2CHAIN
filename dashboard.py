import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from io import BytesIO

from db import get_connection, fetch_all

# =====================================================
# BIN2CHAIN - MYSQL ADMIN AND CITIZEN DASHBOARD
# =====================================================

BASE_DIR = Path(__file__).parent
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

STATUS_OPTIONS = ["Submitted", "In Progress", "Resolved"]

DEPARTMENTS = [
    "Road Maintenance Department",
    "Sanitation Department",
    "Water Supply Department",
    "Drainage Department",
    "Electrical Department",
    "Public Safety Department",
    "General Administration"
]

PRIORITIES = ["Low", "Medium", "High", "Critical"]

REVIEW_OPTIONS = [
    "Pending Review",
    "Accepted",
    "Rejected"
]


def current_timestamp():
    return datetime.now().replace(tzinfo=None)


# =====================================================
# LOAD COMPLAINTS FROM MYSQL
# =====================================================

def load_reports():

    reports = fetch_all("""
        SELECT
            report_id,
            brand,
            category,
            location,
            description,
            photo,
            status,
            created_at,
            admin_remarks,
            resolution_notes,
            review_status,
            assigned_department,
            assigned_officer,
            priority,
            rejection_reason,
            assignment_remarks,
            latitude,
            longitude,
            gps_accuracy,
            gps_source
        FROM complaints
        ORDER BY created_at DESC
    """)

    for report in reports:

        report["status_history"] = fetch_all("""
            SELECT
                status,
                remarks,
                changed_at AS timestamp,
                changed_by
            FROM complaint_status_history
            WHERE report_id = %s
            ORDER BY changed_at ASC, id ASC
        """, (report["report_id"],))

        report["assignment_history"] = fetch_all("""
            SELECT
                ca.officer_name AS assigned_officer,
                ca.priority,
                ca.remarks AS assignment_remarks,
                ca.assigned_at AS timestamp,
                ca.assignment_status AS review_status,
                d.department_name AS assigned_department
            FROM complaint_assignments ca
            LEFT JOIN departments d
                ON ca.department_id = d.department_id
            WHERE ca.report_id = %s
            ORDER BY ca.assigned_at ASC, ca.assignment_id ASC
        """, (report["report_id"],))

        report.setdefault("status", "Submitted")
        report.setdefault("admin_remarks", "")
        report.setdefault("resolution_notes", "")
        report.setdefault("review_status", "Pending Review")
        report.setdefault("assigned_department", "")
        report.setdefault("assigned_officer", "")
        report.setdefault("priority", "Medium")
        report.setdefault("rejection_reason", "")
        report.setdefault("assignment_remarks", "")

    return reports


# =====================================================
# DATAFRAME
# =====================================================

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

    for column, value in defaults.items():

        if column not in df.columns:
            df[column] = value

        df[column] = df[column].fillna(value)

    return df


# =====================================================
# PHOTO HELPER
# =====================================================

def get_photo(photo_path):

    if not photo_path:
        return None

    path = Path(photo_path)

    if not path.is_absolute():
        path = BASE_DIR / path

    if path.is_file():
        return path

    return None


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

    submitted = int(
        (df["status"] == "Submitted").sum()
    )

    in_progress = int(
        (df["status"] == "In Progress").sum()
    )

    resolved = int(
        (df["status"] == "Resolved").sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Reports", total)
    col2.metric("Submitted", submitted)
    col3.metric("In Progress", in_progress)
    col4.metric("Resolved", resolved)

    st.divider()

    st.subheader("📋 All Reports")

    st.dataframe(
        df[
            [
                "report_id",
                "category",
                "location",
                "status",
                "created_at"
            ]
        ],
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

        if (
            username.strip().lower() == "admin"
            and password == ADMIN_PASSWORD
        ):

            st.session_state.admin_authenticated = True

            st.success("Login successful!")

            st.rerun()

        else:

            st.error("Invalid username or password.")


# =====================================================
# SAVE DEPARTMENT ASSIGNMENT TO MYSQL
# =====================================================

def save_municipal_assignment(report_id, values):

    connection = get_connection()

    if connection is None:
        return False, "MySQL connection failed."

    cursor = None

    try:

        cursor = connection.cursor()

        department_name = values["assigned_department"]

        department_id = None

        if department_name:

            cursor.execute("""
                SELECT department_id
                FROM departments
                WHERE department_name = %s
            """, (department_name,))

            result = cursor.fetchone()

            if result:
                department_id = result[0]

            else:

                cursor.execute("""
                    INSERT INTO departments
                    (department_name)
                    VALUES (%s)
                """, (department_name,))

                department_id = cursor.lastrowid

        cursor.execute("""
            UPDATE complaints
            SET
                review_status = %s,
                assigned_department = %s,
                assigned_officer = %s,
                priority = %s,
                rejection_reason = %s,
                assignment_remarks = %s
            WHERE report_id = %s
        """, (
            values["review_status"],
            department_name or None,
            values["assigned_officer"] or None,
            values["priority"],
            values["rejection_reason"] or None,
            values["assignment_remarks"] or None,
            report_id
        ))

        if cursor.rowcount == 0:

            cursor.execute("""
                SELECT report_id
                FROM complaints
                WHERE report_id = %s
            """, (report_id,))

            if cursor.fetchone() is None:
                raise ValueError("Complaint not found.")

        cursor.execute("""
            INSERT INTO complaint_assignments (
                report_id,
                department_id,
                officer_name,
                priority,
                remarks,
                assigned_at,
                assignment_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            report_id,
            department_id,
            values["assigned_officer"] or None,
            values["priority"],
            values["assignment_remarks"] or None,
            current_timestamp(),
            values["review_status"]
        ))

        connection.commit()

        return True, None

    except Exception as error:

        connection.rollback()

        return False, str(error)

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =====================================================
# UPDATE COMPLAINT STATUS IN MYSQL
# =====================================================

def save_complaint_status(
    report_id,
    old_status,
    new_status,
    admin_remarks,
    resolution_notes
):

    connection = get_connection()

    if connection is None:
        return False, "MySQL connection failed."

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            UPDATE complaints
            SET
                status = %s,
                admin_remarks = %s,
                resolution_notes = %s
            WHERE report_id = %s
        """, (
            new_status,
            admin_remarks,
            resolution_notes,
            report_id
        ))

        if cursor.rowcount == 0:

            cursor.execute("""
                SELECT report_id
                FROM complaints
                WHERE report_id = %s
            """, (report_id,))

            if cursor.fetchone() is None:
                raise ValueError("Complaint not found.")

        cursor.execute("""
            INSERT INTO complaint_status_history (
                report_id,
                status,
                remarks,
                changed_at,
                changed_by
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            report_id,
            new_status,
            admin_remarks or resolution_notes or None,
            current_timestamp(),
            "admin"
        ))

        connection.commit()

        return True, None

    except Exception as error:

        connection.rollback()

        return False, str(error)

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =====================================================
# MUNICIPAL DEPARTMENT ASSIGNMENT
# =====================================================

def render_department_assignment(reports):

    st.divider()

    st.header("🏛️ Municipal Complaint Management")

    st.caption(
        "Verify citizen complaints, assign departments "
        "and officers, and manage priority."
    )

    valid_reports = [
        report for report in reports
        if report.get("report_id")
    ]

    if not valid_reports:

        st.info("No complaints available.")

        return

    report_ids = [
        str(report["report_id"])
        for report in valid_reports
    ]

    selected_id = st.selectbox(
        "Select Complaint for Municipal Review",
        report_ids,
        key="municipal_assignment_report"
    )

    report = next(
        (
            item for item in valid_reports
            if str(item["report_id"]) == selected_id
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

    current_review = report.get("review_status") or "Pending Review"

    if current_review not in REVIEW_OPTIONS:
        current_review = "Pending Review"

    department_options = ["Not Assigned"] + DEPARTMENTS

    current_department = (
        report.get("assigned_department") or "Not Assigned"
    )

    if current_department not in department_options:
        department_options.append(current_department)

    current_priority = report.get("priority") or "Medium"

    if current_priority not in PRIORITIES:
        current_priority = "Medium"

    st.markdown("### 🏛️ Verification and Department Assignment")

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
                "assigned_department": (
                    "" if department == "Not Assigned"
                    else department
                ),
                "assigned_officer": officer.strip(),
                "priority": priority,
                "rejection_reason": rejection_reason.strip(),
                "assignment_remarks": remarks.strip()
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

        history_df = pd.DataFrame(history)

        columns = [
            col for col in [
                "timestamp",
                "review_status",
                "assigned_department",
                "assigned_officer",
                "priority",
                "assignment_remarks"
            ]
            if col in history_df.columns
        ]

        st.dataframe(
            history_df[columns],
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

    # OVERVIEW

    st.subheader("📊 Complaint Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Reports", total)
    col2.metric("Submitted", submitted)
    col3.metric("In Progress", in_progress)
    col4.metric("Resolved", resolved)

    st.divider()

    # SEARCH AND FILTER

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

        mask = (
            filtered_df[
                ["report_id", "location", "description"]
            ]
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

    # MUNICIPAL MODULE

    render_department_assignment(reports)

    # EXPORT

    st.divider()

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
                "Install using: pip install openpyxl"
            )

    # STATUS MANAGEMENT

    st.divider()

    st.subheader("✏️ Manage Complaint Status")

    report_ids = [
        str(report["report_id"])
        for report in reports
        if report.get("report_id")
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
            report for report in reports
            if str(report["report_id"]) == selected_id
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

    photo_file = get_photo(selected_report.get("photo"))

    if photo_file:

        st.image(
            str(photo_file),
            caption="Citizen Uploaded Photo",
            use_container_width=True
        )

    # UPDATE STATUS

    st.divider()

    st.markdown("### 📝 Update Complaint")

    current_status = (
        selected_report.get("status") or "Submitted"
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
                "Please enter Resolution Notes before marking "
                "a complaint as Resolved."
            )

        else:

            old_status = (
                selected_report.get("status") or "Submitted"
            )

            old_remarks = (
                selected_report.get("admin_remarks") or ""
            )

            old_resolution = (
                selected_report.get("resolution_notes") or ""
            )

            changed = (
                old_status != new_status
                or old_remarks != admin_remarks.strip()
                or old_resolution != resolution_notes.strip()
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

    # STATUS HISTORY

    st.divider()

    st.subheader("🕒 Complaint History")

    history = selected_report.get("status_history", [])

    if history:

        history_df = pd.DataFrame(history)

        columns = [
            col for col in [
                "timestamp",
                "status",
                "remarks",
                "changed_by"
            ]
            if col in history_df.columns
        ]

        st.dataframe(
            history_df[columns],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No status history available yet. "
            "History will be recorded after the first admin update."
        )

    # CATEGORY ANALYSIS

    st.divider()

    st.subheader("📈 Complaint Category Analysis")

    category_counts = df["category"].value_counts()

    if not category_counts.empty:
        st.bar_chart(category_counts)

    # STATUS ANALYSIS

    st.subheader("📊 Status Analysis")

    status_counts = (
        df["status"]
        .value_counts()
        .reindex(STATUS_OPTIONS, fill_value=0)
    )

    st.bar_chart(status_counts)

    # ADMIN SUMMARY

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

        st.metric(
            "Open Complaints",
            submitted + in_progress
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

    col1, col2 = st.columns([4, 1])

    with col1:
        st.title("🌱 Bin2Chain Administration")

    with col2:

        if st.button("Logout", use_container_width=True):

            st.session_state.admin_authenticated = False

            st.rerun()

    st.divider()

    render_admin_dashboard()