
import json
from pathlib import Path
from datetime import datetime

from db import get_connection


JSON_FILE = Path("data/reports.json")


def convert_datetime(value):
    """Convert ISO datetime into MySQL-compatible datetime."""
    if not value:
        return None

    dt = datetime.fromisoformat(value)

    # Preserve the local clock time and remove timezone info.
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    return dt


def get_department_id(cursor, department_name):
    """Find a department or create it if it does not exist."""
    if not department_name:
        return None

    cursor.execute(
        "SELECT department_id FROM departments WHERE department_name = %s",
        (department_name,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        "INSERT INTO departments (department_name) VALUES (%s)",
        (department_name,)
    )

    return cursor.lastrowid


def migrate():
    if not JSON_FILE.exists():
        print(f"JSON file not found: {JSON_FILE}")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        reports = json.load(file)

    if not isinstance(reports, list):
        print("Invalid JSON format. Expected a list of complaints.")
        return

    connection = get_connection()

    if connection is None:
        print("MySQL connection failed.")
        return

    cursor = None

    migrated = 0
    skipped = 0

    try:
        cursor = connection.cursor()

        for report in reports:
            report_id = report.get("report_id")

            if not report_id:
                print("Skipping record without report_id.")
                skipped += 1
                continue

            # Prevent duplicate complaints.
            cursor.execute(
                "SELECT report_id FROM complaints WHERE report_id = %s",
                (report_id,)
            )

            if cursor.fetchone():
                print(f"Already exists, skipped: {report_id}")
                skipped += 1
                continue

            # 1. Insert complaint.
            cursor.execute(
                """
                INSERT INTO complaints (
                    report_id, brand, category, location,
                    description, photo, status, created_at,
                    admin_remarks, resolution_notes, review_status,
                    assigned_department, assigned_officer, priority,
                    rejection_reason, assignment_remarks,
                    latitude, longitude, gps_accuracy, gps_source
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    report_id,
                    report.get("brand"),
                    report.get("category"),
                    report.get("location"),
                    report.get("description"),
                    report.get("photo"),
                    report.get("status", "Submitted"),
                    convert_datetime(report.get("created_at")),
                    report.get("admin_remarks"),
                    report.get("resolution_notes"),
                    report.get("review_status", "Pending Review"),
                    report.get("assigned_department"),
                    report.get("assigned_officer"),
                    report.get("priority"),
                    report.get("rejection_reason"),
                    report.get("assignment_remarks"),
                    report.get("latitude"),
                    report.get("longitude"),
                    report.get("gps_accuracy"),
                    report.get("gps_source")
                )
            )

            # 2. Insert status history.
            for history in report.get("status_history", []):
                cursor.execute(
                    """
                    INSERT INTO complaint_status_history (
                        report_id, status, remarks,
                        changed_at, changed_by
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        report_id,
                        history.get("status"),
                        history.get("remarks"),
                        convert_datetime(history.get("timestamp")),
                        None
                    )
                )

            # 3. Insert assignment history.
            assignments = report.get("assignment_history", [])

            # Fallback: preserve current assignment if history is empty.
            if not assignments and report.get("assigned_department"):
                assignments = [{
                    "review_status": report.get("review_status"),
                    "assigned_department": report.get("assigned_department"),
                    "assigned_officer": report.get("assigned_officer"),
                    "priority": report.get("priority"),
                    "assignment_remarks": report.get("assignment_remarks"),
                    "timestamp": report.get("created_at")
                }]

            for assignment in assignments:
                department_name = assignment.get("assigned_department")

                department_id = get_department_id(
                    cursor, department_name
                )

                cursor.execute(
                    """
                    INSERT INTO complaint_assignments (
                        report_id, department_id, officer_name,
                        priority, remarks, assigned_at,
                        assignment_status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        report_id,
                        department_id,
                        assignment.get("assigned_officer"),
                        assignment.get("priority"),
                        assignment.get("assignment_remarks"),
                        convert_datetime(assignment.get("timestamp")),
                        assignment.get("review_status")
                    )
                )

            migrated += 1
            print(f"Migrated successfully: {report_id}")

        connection.commit()

        print("\n========== MIGRATION SUMMARY ==========")
        print(f"Total JSON complaints: {len(reports)}")
        print(f"New complaints migrated: {migrated}")
        print(f"Skipped complaints: {skipped}")
        print("Migration completed successfully.")

    except Exception as error:
        connection.rollback()
        print(f"Migration failed. Transaction rolled back: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


if __name__ == "__main__":
    migrate()
