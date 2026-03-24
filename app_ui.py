"""
Flight Fare Prediction - Streamlit UI
Run: streamlit run app_ui.py
Make sure Flask API (app.py) is running on port 5000 first.
"""

import streamlit as st
import requests

API_URL = "http://localhost:5000"

st.set_page_config(
    page_title="Flight Fare Predictor ✈️",
    page_icon="✈️",
    layout="centered"
)

st.title("✈️ Flight Fare Predictor")
st.markdown(
    "Estimate **domestic flight fares** across major Indian cities. "
    "Powered by a Gradient Boosting model trained on 2,000 synthetic booking records."
)
st.divider()

# ─── Fetch options from API ───
try:
    opts = requests.get(f"{API_URL}/options", timeout=5).json()
except Exception:
    st.error("❌ Cannot connect to the API. Make sure `app.py` is running on port 5000.")
    st.stop()

# ─── Input Form ───
with st.form("fare_form"):
    st.markdown("#### 🛫 Flight Details")
    col1, col2 = st.columns(2)

    with col1:
        airline      = st.selectbox("🏷️ Airline", opts["airlines"])
        source_city  = st.selectbox("📍 From", opts["cities"])
        departure_time = st.selectbox("🕐 Departure Time", opts["time_slots"])
        stops        = st.selectbox("🔁 Stops", opts["stops"])

    with col2:
        seat_class       = st.selectbox("💺 Class", opts["classes"])
        destination_city = st.selectbox("🏁 To", [c for c in opts["cities"]])
        arrival_time     = st.selectbox("🕓 Arrival Time", opts["time_slots"])
        days_before      = st.slider("📅 Days Before Departure", 1, 90, 14)

    duration_hours = st.slider("⏱️ Flight Duration (hours)", 0.5, 12.0, 2.0, step=0.5)

    submitted = st.form_submit_button("🔮 Predict Fare", use_container_width=True)

# ─── Prediction ───
if submitted:
    if source_city == destination_city:
        st.warning("⚠️ Source and destination cities cannot be the same.")
    else:
        payload = {
            "airline":               airline,
            "source_city":           source_city,
            "destination_city":      destination_city,
            "departure_time":        departure_time,
            "arrival_time":          arrival_time,
            "stops":                 stops,
            "class":                 seat_class,
            "days_before_departure": days_before,
            "duration_hours":        duration_hours,
        }

        try:
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=5)
            result   = response.json()

            if response.status_code == 200:
                fare    = result["predicted_fare_inr"]
                band    = result["fare_band"]
                summary = result["input_summary"]

                st.success(f"### 💰 Estimated Fare: **{result['formatted']}**")

                # Fare band
                st.markdown("#### 📊 Fare Range")
                st.info(
                    f"Expected range: **₹{band['low']:,}** – **₹{band['high']:,}** (±8%)"
                )

                # Booking tip
                st.markdown("#### 💡 Booking Tip")
                if days_before <= 3:
                    st.warning("🚨 Last-minute booking — fares are at a premium. Book now if you must!")
                elif days_before <= 7:
                    st.warning("⚠️ Less than a week away — prices are rising fast.")
                elif days_before >= 60:
                    st.success("🎉 Great timing! Early booking discounts are likely available.")
                else:
                    st.info("📌 Moderate lead time — fares are typical for this route.")

                # Summary metrics
                st.markdown("#### 🗺️ Trip Summary")
                c1, c2, c3 = st.columns(3)
                c1.metric("Route",    summary["route"])
                c2.metric("Airline",  summary["airline"])
                c3.metric("Class",    summary["class"])

                c1.metric("Stops",    summary["stops"])
                c2.metric("Duration", f"{summary['duration_hours']} hrs")
                c3.metric("Days Left", f"{summary['days_before_departure']} days")

                c1.metric("Departs",  summary["departure_time"])
                c2.metric("Arrives",  summary["arrival_time"])

            else:
                st.error(f"API Error: {result.get('error', 'Unknown error')}")

        except requests.exceptions.ConnectionError:
            st.error("❌ Could not reach the API. Is `app.py` running?")

st.divider()
st.caption("Model: Gradient Boosting Regressor | Dataset: Synthetic Indian Domestic Flight Data 2024")
