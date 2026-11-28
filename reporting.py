import json
import uuid
from pathlib import Path
from datetime import datetime

import streamlit as st

try:
    from gps_location import render_gps_location
except Exception:
    render_gps_location = None

# ==================================================
# BIN2CHAIN | CITIZEN REPORTING MODULE
# JSON DEMO MODE - no MySQL required
# ==================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORT_FILE = DATA_DIR / "reports.json"
UPLOAD_DIR = BASE_DIR / "uploads"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def load_reports():
    if not REPORT_FILE.exists():
        return []
    try:
        with REPORT_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_reports(reports):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = REPORT_FILE.with_suffix(".tmp")
    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(reports, file, ensure_ascii=False, indent=2, default=str)
    temp_file.replace(REPORT_FILE)


def save_report(report):
    reports = load_reports()
    reports.insert(0, report)
    save_reports(reports)
    return True


def render_reporting_form(language="English"):
    hindi = language == "Hindi"
    title = "नागरिक समस्या दर्ज करें" if hindi else "Report a Civic Issue"
    subtitle = (
        "आपकी आवाज़, आपके पड़ोस में बदलाव ला सकती है।"
        if hindi else
        "Your voice can make a difference in your neighbourhood."
    )

    categories = {
        "English": [
            "Road / Pothole", "Garbage / Waste", "Waterlogging",
            "Streetlight", "Water Supply", "Public Safety", "Other"
        ],
        "Hindi": [
            "सड़क / गड्ढा", "कूड़ा / अपशिष्ट", "जलभराव",
            "स्ट्रीट लाइट", "पानी की आपूर्ति", "सार्वजनिक सुरक्षा", "अन्य"
        ],
    }

    st.markdown(
        f"""
        <div style="padding:10px 0 15px 0;">
            <h1 style="color:#123C35;font-size:34px;">📝 {title}</h1>
            <p style="color:#64756F;font-size:17px;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "Help make your community cleaner, safer and better."
        if not hindi else
        "अपने समुदाय को स्वच्छ, सुरक्षित और बेहतर बनाने में सहयोग करें।"
    )

    # GPS component is optional in demo mode. It must stay outside st.form.
    gps_data = None
    if render_gps_location is not None:
        try:
            gps_data = render_gps_location()
        except Exception:
            gps_data = None

    with st.form("Bin2Chain_report_form", clear_on_submit=True):
        category = st.selectbox(
            "समस्या की श्रेणी" if hindi else "Issue Category",
            categories["Hindi" if hindi else "English"],
        )
        photo = st.file_uploader(
            "समस्या की फोटो अपलोड करें" if hindi else "Upload Issue Photo",
            type=["jpg", "jpeg", "png"],
        )
        location = st.text_input(
            "समस्या की लोकेशन" if hindi else "Issue Location",
            placeholder="e.g. Laxmi Nagar, Delhi",
        )
        description = st.text_area(
            "समस्या का विवरण" if hindi else "Describe the Problem",
            max_chars=1000,
            height=150,
        )
        st.caption(
            "Maximum description length: 1000 characters."
            if not hindi else
            "विवरण की अधिकतम सीमा: 1000 अक्षर।"
        )
        submitted = st.form_submit_button(
            "रिपोर्ट जमा करें" if hindi else "Submit Report",
            use_container_width=True,
            type="primary",
        )

    if not submitted:
        return

    if not location.strip():
        st.error("कृपया समस्या की लोकेशन भरें।" if hindi else "Please enter the issue location.")
        return
    if not description.strip():
        st.error("कृपया समस्या का विवरण दें।" if hindi else "Please describe the problem.")
        return
    if photo is not None and photo.size > 10 * 1024 * 1024:
        st.error("फोटो का आकार 10 MB से कम होना चाहिए।" if hindi else "Photo size must be less than 10 MB.")
        return

    report_id = "NAG-" + uuid.uuid4().hex[:8].upper()
    photo_path = None

    try:
        if photo is not None:
            extension = Path(photo.name).suffix.lower()
            if extension not in [".jpg", ".jpeg", ".png"]:
                extension = ".jpg"
            photo_filename = f"{report_id}{extension}"
            saved_photo = UPLOAD_DIR / photo_filename
            saved_photo.write_bytes(photo.getvalue())
            photo_path = str(saved_photo.relative_to(BASE_DIR))

        latitude = gps_data.get("latitude") if isinstance(gps_data, dict) else None
        longitude = gps_data.get("longitude") if isinstance(gps_data, dict) else None
        accuracy = gps_data.get("accuracy") if isinstance(gps_data, dict) else None
        gps_source = gps_data.get("source") if isinstance(gps_data, dict) else None

        report = {
            "report_id": report_id,
            "brand": "Bin2Chain",
            "category": category,
            "location": location.strip(),
            "description": description.strip(),
            "photo": photo_path,
            "latitude": latitude,
            "longitude": longitude,
            "gps_accuracy": accuracy,
            "gps_source": gps_source,
            "status": "Submitted",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "admin_remarks": "",
            "resolution_notes": "",
            "review_status": "Pending Review",
            "assigned_department": "",
            "assigned_officer": "",
            "priority": "Medium",
            "rejection_reason": "",
            "assignment_remarks": "",
            "status_history": [],
            "assignment_history": [],
        }

        save_report(report)
        st.success(
            f"आपकी रिपोर्ट सफलतापूर्वक जमा हुई! ID: {report_id}"
            if hindi else
            f"Your report was submitted successfully! ID: {report_id}"
        )
        if latitude is not None and longitude is not None:
            st.success(
                "GPS coordinates भी complaint के साथ save हो गए।"
                if hindi else
                "GPS coordinates have also been saved with your complaint."
            )
        else:
            st.info(
                "GPS location उपलब्ध नहीं है; आपने जो लोकेशन लिखी है वह सेव हो गई है।"
                if hindi else
                "GPS was not captured; the location you entered has been saved."
            )

        st.markdown(
            f"""
            <div style="
                background:#E8F5EF;
                padding:20px;
                border-radius:12px;
                border-left:5px solid #16865B;
                margin-top:12px;">
                <h3 style="color:#123C35;">🌱 Bin2Chain</h3>
                <p style="color:#315B4D;">Your complaint reference number</p>
                <h2 style="color:#123C35;">{report_id}</h2>
                <p style="color:#315B4D;">Keep this ID for future reference.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception as error:
        if photo_path:
            saved_photo = BASE_DIR / photo_path
            if saved_photo.exists():
                saved_photo.unlink()
        st.error(f"Unable to save your report: {error}")
