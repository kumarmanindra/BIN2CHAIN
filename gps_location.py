
import streamlit as st
from streamlit_geolocation import streamlit_geolocation


def render_gps_location():

    st.subheader("📍 Capture Complaint GPS Location")

    st.caption(
        "Allow browser location permission to capture "
        "the GPS coordinates of the complaint."
    )

    location = streamlit_geolocation()

    if isinstance(location, dict):

        latitude = location.get("latitude")
        longitude = location.get("longitude")

        if latitude is not None and longitude is not None:

            st.session_state["bin2chain_gps"] = {
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": location.get("accuracy"),
                "source": "Browser GPS"
            }

    gps_data = st.session_state.get("bin2chain_gps")

    if gps_data:

        st.success("GPS location captured successfully!")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Latitude",
                f"{gps_data['latitude']:.6f}"
            )

        with col2:
            st.metric(
                "Longitude",
                f"{gps_data['longitude']:.6f}"
            )

        accuracy = gps_data.get("accuracy")

        if accuracy is not None:
            st.caption(
                f"GPS accuracy: approximately {accuracy:.1f} metres"
            )

        map_url = (
            "https://www.google.com/maps?q="
            f"{gps_data['latitude']},{gps_data['longitude']}"
        )

        st.markdown(
            f"[📍 View captured location on Google Maps]({map_url})"
        )

        if st.button("Remove captured GPS location"):
            st.session_state.pop("bin2chain_gps", None)
            st.rerun()

        return gps_data

    st.warning(
        "GPS location not captured yet. "
        "Allow browser location permission when prompted."
    )

    return None
