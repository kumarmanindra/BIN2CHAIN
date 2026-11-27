
import streamlit as st
import json
import uuid
from pathlib import Path
from datetime import datetime
from gps_location import render_gps_location

# ==================================================
# Bin2Chain | CITIZEN REPORTING MODULE
# ==================================================

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
REPORT_FILE = DATA_DIR / "reports.json"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# SAVE REPORT
# ==================================================

def save_report(report):
    reports = []

    if REPORT_FILE.exists():
        try:
            reports = json.loads(
                REPORT_FILE.read_text(encoding="utf-8")
            )
            if not isinstance(reports, list):
                reports = []
        except (json.JSONDecodeError, OSError):
            reports = []

    reports.append(report)

    REPORT_FILE.write_text(
        json.dumps(
            reports,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


# ==================================================
# CITIZEN REPORTING FORM
# ==================================================

def render_reporting_form(language="English"):

    hindi = language == "Hindi"

    title = (
        "नागरिक समस्या दर्ज करें"
        if hindi else "Report a Civic Issue"
    )

    subtitle = (
        "आपकी आवाज़, आपके पड़ोस में बदलाव ला सकती है।"
        if hindi else
        "Your voice can make a difference in your neighbourhood."
    )

    categories = {
        "English": [
            "Road / Pothole",
            "Garbage / Waste",
            "Waterlogging",
            "Streetlight",
            "Water Supply",
            "Public Safety",
            "Other"
        ],
        "Hindi": [
            "सड़क / गड्ढा",
            "कूड़ा / अपशिष्ट",
            "जलभराव",
            "स्ट्रीट लाइट",
            "पानी की आपूर्ति",
            "सार्वजनिक सुरक्षा",
            "अन्य"
        ]
    }

    st.markdown(
        f"""
        <div style="padding:10px 0 15px 0;">
            <h1 style="color:#123C35;font-size:34px;">
                📝 {title}
            </h1>
            <p style="color:#64756F;font-size:17px;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Help make your community cleaner, safer and better."
        if not hindi else
        "अपने समुदाय को स्वच्छ, सुरक्षित और बेहतर बनाने में सहयोग करें।"
    )

    # GPS must be outside st.form
    gps_data = render_gps_location()

    # ==================================================
    # REPORT FORM
    # ==================================================

    with st.form(
        "Bin2Chain_report_form",
        clear_on_submit=True
    ):

        category = st.selectbox(
            "समस्या की श्रेणी" if hindi else "Issue Category",
            categories["Hindi" if hindi else "English"]
        )

        photo = st.file_uploader(
            "समस्या की फोटो अपलोड करें"
            if hindi else "Upload Issue Photo",
            type=["jpg", "jpeg", "png"]
        )

        location = st.text_input(
            "समस्या की लोकेशन" if hindi else "Issue Location",
            placeholder="e.g. Laxmi Nagar, Delhi"
        )

        description = st.text_area(
            "समस्या का विवरण" if hindi else "Describe the Problem",
            max_chars=1000,
            height=150
        )

        st.caption(
            "Maximum description length: 1000 characters."
            if not hindi else
            "विवरण की अधिकतम सीमा: 1000 अक्षर।"
        )

        submitted = st.form_submit_button(
            "रिपोर्ट जमा करें" if hindi else "Submit Report",
            use_container_width=True,
            type="primary"
        )

        if submitted:

            if not location.strip():
                st.error(
                    "कृपया समस्या की लोकेशन भरें।"
                    if hindi else
                    "Please enter the issue location."
                )

            elif not description.strip():
                st.error(
                    "कृपया समस्या का विवरण दें।"
                    if hindi else
                    "Please describe the problem."
                )

            elif photo is not None and photo.size > 10 * 1024 * 1024:
                st.error(
                    "फोटो का आकार 10 MB से कम होना चाहिए।"
                    if hindi else
                    "Photo size must be less than 10 MB."
                )

            else:

                report_id = (
                    "NAG-" + uuid.uuid4().hex[:8].upper()
                )

                photo_path = None

                if photo is not None:
                    extension = Path(photo.name).suffix.lower()
                    photo_filename = f"{report_id}{extension}"
                    photo_path = UPLOAD_DIR / photo_filename
                    photo_path.write_bytes(photo.getvalue())

                # GPS coordinates
                latitude = (
                    gps_data.get("latitude")
                    if gps_data else None
                )

                longitude = (
                    gps_data.get("longitude")
                    if gps_data else None
                )

                accuracy = (
                    gps_data.get("accuracy")
                    if gps_data else None
                )

                # Complaint record
                report = {
                    "report_id": report_id,
                    "brand": "Bin2Chain",
                    "category": category,
                    "location": location.strip(),
                    "description": description.strip(),
                    "photo": str(photo_path) if photo_path else None,
                    "latitude": latitude,
                    "longitude": longitude,
                    "gps_accuracy": accuracy,
                    "gps_source": (
                        gps_data.get("source")
                        if gps_data else None
                    ),
                    "status": "Submitted",
                    "created_at": datetime.now().astimezone().isoformat()
                }

                try:
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
                        st.warning(
                            "इस complaint के साथ GPS location save नहीं हुई।"
                            if hindi else
                            "GPS location was not captured for this complaint."
                        )

                    st.markdown(
                        f"""
                        <div style="
                            background:#E8F5EF;
                            padding:20px;
                            border-radius:12px;
                            border-left:5px solid #16865B;
                            margin-top:12px;
                        ">
                            <h3 style="color:#123C35;">🌱 Bin2Chain</h3>
                            <p style="color:#315B4D;">
                                Your complaint reference number
                            </p>
                            <h2 style="color:#123C35;">{report_id}</h2>
                            <p style="color:#315B4D;">
                                Keep this ID for future reference.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                except (OSError, TypeError, ValueError) as error:
                    st.error(
                        f"Unable to save your report: {error}"
                    )
