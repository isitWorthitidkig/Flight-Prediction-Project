"""
Flight Fare Prediction - Streamlit UI
Run: streamlit run app_ui.py
Make sure Flask API (app.py) is running on port 5000 first.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import random
from streamlit_extras.metric_cards import style_metric_cards

API_URL = "http://localhost:5000"

st.set_page_config(
    page_title="SkyFare — Flight Fare Predictor",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS ───
st.markdown("""
<style>

/* Confetti */
@keyframes confetti-fall {
    0%   { transform: translateY(-10px) rotate(0deg);   opacity: 1; }
    100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
}
.confetti-piece {
    position: fixed;
    width: 10px; height: 10px;
    top: -10px;
    animation: confetti-fall linear forwards;
    z-index: 9999;
    border-radius: 2px;
}

/* Skeleton shimmer */
@keyframes shimmer {
    0%   { background-position: -800px 0; }
    100% { background-position:  800px 0; }
}
.skeleton {
    background: linear-gradient(90deg,
        rgba(99,179,237,0.05) 25%,
        rgba(99,179,237,0.15) 50%,
        rgba(99,179,237,0.05) 75%);
    background-size: 800px 100%;
    animation: shimmer 1.4s infinite;
    border-radius: 10px;
}
.skeleton-title  { height: 2.5rem; width: 60%; margin: 0 auto 1rem; }
.skeleton-line   { height: 0.9rem; width: 80%; margin: 0.5rem auto; }
.skeleton-line-s { height: 0.9rem; width: 50%; margin: 0.5rem auto; }
.skeleton-box    { height: 5rem;   width: 100%; margin: 0.8rem 0; }
.skeleton-wrap {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(99,179,237,0.1);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2e 50%, #0a1628 100%);
    color: #e8eaf0;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1200px; }

/* Starfield */
#starfield {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
}
.star {
    position: absolute;
    background: white;
    border-radius: 50%;
    animation: twinkle linear infinite;
}
@keyframes twinkle {
    0%   { opacity: 0;   transform: translateY(0px); }
    50%  { opacity: 1; }
    100% { opacity: 0;   transform: translateY(-20px); }
}

/* Ensure content is above starfield */
.block-container { position: relative; z-index: 1; }

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #1a2744 0%, #0f1e35 60%, #162040 100%);
    border: 1px solid rgba(99, 179, 237, 0.2);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '✈';
    position: absolute;
    right: 2rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 8rem;
    opacity: 0.05;
}
.hero h1 {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #63b3ed, #90cdf4, #bee3f8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem 0;
}
.hero p { color: #90adc4; font-size: 1rem; margin: 0; }

/* Orbiting plane on card hover */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}
.card-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #63b3ed;
    margin-bottom: 1rem;
}

/* Fare result */
.fare-result {
    background: linear-gradient(135deg, #1a3a5c 0%, #0f2a45 100%);
    border: 1px solid rgba(99,179,237,0.4);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    margin: 1rem 0;
}
.fare-amount {
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, #63b3ed, #90cdf4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
}
.fare-label { color: #90adc4; font-size: 0.85rem; margin-top: 0.5rem; }

/* Route display */
.route-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 1.2rem 2rem;
    background: rgba(99,179,237,0.08);
    border-radius: 12px;
    margin: 1rem 0;
}
.city-code { font-size: 2rem; font-weight: 700; color: #bee3f8; }
.route-line {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #63b3ed;
    font-size: 1.2rem;
}
.route-line hr { flex: 1; border: 1px dashed rgba(99,179,237,0.4); }

/* Tip badges */
.tip-danger {
    background: rgba(245,101,101,0.15);
    border: 1px solid rgba(245,101,101,0.4);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    color: #fc8181;
}
.tip-warning {
    background: rgba(237,137,54,0.15);
    border: 1px solid rgba(237,137,54,0.4);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    color: #f6ad55;
}
.tip-success {
    background: rgba(72,187,120,0.15);
    border: 1px solid rgba(72,187,120,0.4);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    color: #68d391;
}
.tip-info {
    background: rgba(99,179,237,0.1);
    border: 1px solid rgba(99,179,237,0.3);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    color: #90cdf4;
}

/* Metric cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.8rem;
    margin-top: 0.5rem;
}
.metric-item {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(99,179,237,0.1);
    border-radius: 10px;
    padding: 0.8rem 1rem;
}
.metric-item .label { font-size: 0.7rem; color: #718096; text-transform: uppercase; letter-spacing: 1px; }
.metric-item .value { font-size: 0.95rem; font-weight: 600; color: #e2e8f0; margin-top: 0.2rem; }

/* Selectbox & slider overrides */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(99,179,237,0.2) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
.stSlider > div { color: #e2e8f0; }

/* Submit button */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #2b6cb0, #3182ce) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.5px;
}
.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #3182ce, #4299e1) !important;
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(49,130,206,0.4) !important;
}

/* Section labels */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #63b3ed;
    margin-bottom: 0.8rem;
    margin-top: 1.2rem;
}

/* Divider */
.custom-divider {
    border: none;
    border-top: 1px solid rgba(99,179,237,0.1);
    margin: 1.5rem 0;
}

/* Pulse ring on fare */
@keyframes pulse-ring {
    0%   { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(99,179,237,0.4); }
    70%  { transform: scale(1);    box-shadow: 0 0 0 12px rgba(99,179,237,0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(99,179,237,0); }
}
.fare-result { animation: pulse-ring 2.5s ease-out 3; }

/* Savings badge */
.savings-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(72,187,120,0.2), rgba(72,187,120,0.1));
    border: 1px solid rgba(72,187,120,0.5);
    border-radius: 20px;
    padding: 0.3rem 1rem;
    font-size: 0.8rem;
    color: #68d391;
    font-weight: 600;
    margin-top: 0.5rem;
}

/* Footer */
.footer {
    text-align: center;
    color: #4a5568;
    font-size: 0.78rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(99,179,237,0.08);
}
</style>
""", unsafe_allow_html=True)

# ─── Starfield ───
stars_html = '<div id="starfield">'
for i in range(150):
    size = round(random.uniform(1, 3), 1)
    top  = random.randint(0, 100)
    left = random.randint(0, 100)
    dur  = round(random.uniform(3, 8), 1)
    delay= round(random.uniform(0, 6), 1)
    stars_html += f'<div class="star" style="width:{size}px;height:{size}px;top:{top}%;left:{left}%;animation-duration:{dur}s;animation-delay:{delay}s;"></div>'
stars_html += '</div>'
st.markdown(stars_html, unsafe_allow_html=True)

# ─── Hero ───
st.markdown("""
<div class="hero">
    <h1>SkyFare ✈️</h1>
    <p>AI-powered domestic flight fare predictor for Indian routes · Gradient Boosting · R² 0.98</p>
    <div style="display:flex;gap:2rem;margin-top:1.2rem;">
        <div style="color:#4a6fa5;font-size:0.8rem;">🛫 <span style="color:#63b3ed;font-weight:600;">10</span> Cities</div>
        <div style="color:#4a6fa5;font-size:0.8rem;">🏷️ <span style="color:#63b3ed;font-weight:600;">6</span> Airlines</div>
        <div style="color:#4a6fa5;font-size:0.8rem;">📊 <span style="color:#63b3ed;font-weight:600;">2,000</span> Records</div>
        <div style="color:#4a6fa5;font-size:0.8rem;">🎯 R² <span style="color:#68d391;font-weight:600;">0.98</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Fetch options ───
try:
    opts = requests.get(f"{API_URL}/options", timeout=5).json()
except Exception:
    st.markdown("""
    <div class="tip-danger">
        ❌ Cannot connect to the API. Make sure <code>app.py</code> is running on port 5000.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── Layout: Form | Results ───
left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🛫 Flight Details</div>', unsafe_allow_html=True)

    with st.form("fare_form"):
        c1, c2 = st.columns(2)
        with c1:
            source_city    = st.selectbox("From 📍", opts["cities"], key="src")
            airline        = st.selectbox("Airline 🏷️", opts["airlines"])
            departure_time = st.selectbox("Departure 🕐", opts["time_slots"])
            stops          = st.selectbox("Stops 🔁", opts["stops"])
        with c2:
            destination_city = st.selectbox("To 🏁", opts["cities"], index=1, key="dst")
            seat_class       = st.selectbox("Class 💺", opts["classes"])
            arrival_time     = st.selectbox("Arrival 🕓", opts["time_slots"], index=2)
            days_before      = st.slider("Days Before Departure 📅", 1, 90, 14)

        duration_hours = st.slider("Flight Duration (hours) ⏱️", 0.5, 12.0, 2.0, step=0.5)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✈️  Predict Fare", use_container_width=True)  # noqa

    st.markdown('</div>', unsafe_allow_html=True)

# ─── Results Panel ───
with right:
    if not submitted:
        st.markdown("""
        <div style="height:100%; display:flex; flex-direction:column; align-items:center;
                    justify-content:center; padding: 3rem 1rem; text-align:center;
                    border: 1px dashed rgba(99,179,237,0.15); border-radius:16px;">
            <div style="font-size:4rem; margin-bottom:1rem;">✈️</div>
            <div style="color:#4a6fa5; font-size:1rem; font-weight:500;">Fill in flight details</div>
            <div style="color:#2d4a6e; font-size:0.85rem; margin-top:0.5rem;">and click Predict Fare</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if source_city == destination_city:
            st.markdown('<div class="tip-danger">⚠️ Source and destination cities cannot be the same.</div>', unsafe_allow_html=True)
        else:
            payload = {
                "airline": airline,
                "source_city": source_city,
                "destination_city": destination_city,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "stops": stops,
                "class": seat_class,
                "days_before_departure": days_before,
                "duration_hours": duration_hours,
            }

            try:
                skel = st.empty()
                skel.markdown("""
                <div class="skeleton-wrap">
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-line"></div>
                    <div class="skeleton skeleton-line-s"></div>
                    <div class="skeleton skeleton-box"></div>
                    <div class="skeleton skeleton-line"></div>
                </div>
                """, unsafe_allow_html=True)
                response = requests.post(f"{API_URL}/predict", json=payload, timeout=5)
                skel.empty()
                result = response.json()

                if response.status_code == 200:
                    fare    = result["predicted_fare_inr"]
                    band    = result["fare_band"]
                    summary = result["input_summary"]

                    # ── Confetti if cheap fare ──
                    cheap_threshold = band["low"] * 0.95
                    if fare <= cheap_threshold:
                        pieces = ""
                        colors = ["#63b3ed","#68d391","#f6ad55","#fc8181","#b794f4","#76e4f7"]
                        for i in range(60):
                            left = random.randint(0, 100)
                            delay = round(random.uniform(0, 2), 2)
                            duration = round(random.uniform(2, 4), 2)
                            color = random.choice(colors)
                            size = random.randint(6, 12)
                            pieces += f'<div class="confetti-piece" style="left:{left}vw;background:{color};width:{size}px;height:{size}px;animation-duration:{duration}s;animation-delay:{delay}s;"></div>'
                        st.markdown(f'<div>{pieces}</div><div class="tip-success" style="text-align:center;font-size:1rem;font-weight:600;margin-bottom:0.5rem">🎉 Great deal! This is a cheap fare for this route!</div>', unsafe_allow_html=True)

                    # ── Fare Result ──
                    savings = result.get("predicted_fare_inr", 0)
                    biz_est = int(savings * 2.8)
                    # find most expensive airline for savings calc
                    try:
                        max_airline_fare = max(
                            requests.post(f"{API_URL}/predict", json={**payload, "airline": al}, timeout=2).json().get("predicted_fare_inr", fare)
                            for al in opts["airlines"]
                        )
                        saved = max_airline_fare - fare
                        savings_html = f'<div class="savings-badge">💰 Save up to ₹{saved:,} vs most expensive airline</div>' if saved > 0 else ""
                    except:
                        savings_html = ""
                    st.markdown(f"""
                    <div class="fare-result">
                        <div class="fare-label">ESTIMATED FARE</div>
                        <div class="fare-amount">{result['formatted']}</div>
                        <div class="fare-label" style="margin-top:0.8rem;">
                            Range: ₹{band['low']:,} – ₹{band['high']:,}
                        </div>
                        {savings_html}
                        <div style="margin-top:1rem;display:flex;justify-content:center;gap:1.5rem;">
                            <div style="background:rgba(72,187,120,0.15);border:1px solid rgba(72,187,120,0.3);border-radius:8px;padding:0.4rem 1rem;font-size:0.78rem;color:#68d391;">✅ Economy</div>
                            <div style="background:rgba(246,173,85,0.1);border:1px solid rgba(246,173,85,0.2);border-radius:8px;padding:0.4rem 1rem;font-size:0.78rem;color:#f6ad55;">Business ~₹{biz_est:,}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Route Display ──
                    src_code = source_city[:3].upper()
                    dst_code = destination_city[:3].upper()
                    stop_icon = "🟢" if stops == "non-stop" else ("🟡" if stops == "1 stop" else "🔴")
                    st.markdown(f"""
                    <div class="route-bar">
                        <div>
                            <div class="city-code">{src_code}</div>
                            <div style="color:#4a6fa5;font-size:0.75rem;text-align:center">{source_city}</div>
                        </div>
                        <div class="route-line">
                            <hr/>{stop_icon}<hr/>
                        </div>
                        <div>
                            <div class="city-code">{dst_code}</div>
                            <div style="color:#4a6fa5;font-size:0.75rem;text-align:center">{destination_city}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Booking Tip ──
                    if days_before <= 3:
                        tip_class, tip_text = "tip-danger", "🚨 Last-minute booking — fares are at a premium. Book now if you must!"
                    elif days_before <= 7:
                        tip_class, tip_text = "tip-warning", "⚠️ Less than a week away — prices are rising fast."
                    elif days_before >= 60:
                        tip_class, tip_text = "tip-success", "🎉 Great timing! Early booking discounts are likely available."
                    else:
                        tip_class, tip_text = "tip-info", "📌 Moderate lead time — fares are typical for this route."

                    st.markdown(f'<div class="{tip_class}" style="margin:0.8rem 0">{tip_text}</div>', unsafe_allow_html=True)

                    # ── Trip Metrics ──
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Airline", airline)
                    m2.metric("Class", seat_class)
                    m3.metric("Stops", stops)
                    m4, m5, m6 = st.columns(3)
                    m4.metric("Duration", f"{duration_hours} hrs")
                    m5.metric("Days Left", f"{days_before} days")
                    m6.metric("Departure", departure_time.split('(')[0].strip())
                    style_metric_cards(
                        background_color="rgba(255,255,255,0.03)",
                        border_left_color="#63b3ed",
                        border_color="rgba(99,179,237,0.15)",
                        box_shadow=False,
                    )

                else:
                    st.markdown(f'<div class="tip-danger">❌ {result.get("error", "Unknown error")}</div>', unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                st.markdown('<div class="tip-danger">❌ Could not reach the API. Is app.py running?</div>', unsafe_allow_html=True)

# ─── Gauge + Charts Section ───
if submitted and source_city != destination_city:
    try:
        result
        if response.status_code == 200:
            st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

            # ── Fare Gauge full width ──
            st.markdown('<div class="section-label">🎯 Fare Position — Cheap vs Expensive for this Route</div>', unsafe_allow_html=True)
            all_fares_sample = []
            for al in opts["airlines"]:
                for s in opts["stops"]:
                    try:
                        r = requests.post(f"{API_URL}/predict", json={**payload, "airline": al, "stops": s}, timeout=2).json()
                        all_fares_sample.append(r.get("predicted_fare_inr", fare))
                    except:
                        pass
            min_f = min(all_fares_sample) if all_fares_sample else int(fare * 0.5)
            max_f = max(all_fares_sample) if all_fares_sample else int(fare * 2)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=fare,
                number={"prefix": "₹", "font": {"color": "#90cdf4", "size": 32}},
                gauge={
                    "axis": {"range": [min_f, max_f], "tickcolor": "#4a6fa5", "tickfont": {"color": "#4a6fa5", "size": 11}},
                    "bar": {"color": "#63b3ed", "thickness": 0.3},
                    "bgcolor": "rgba(0,0,0,0)",
                    "bordercolor": "rgba(99,179,237,0.2)",
                    "steps": [
                        {"range": [min_f, min_f + (max_f-min_f)*0.33], "color": "rgba(72,187,120,0.2)"},
                        {"range": [min_f + (max_f-min_f)*0.33, min_f + (max_f-min_f)*0.66], "color": "rgba(246,173,85,0.2)"},
                        {"range": [min_f + (max_f-min_f)*0.66, max_f], "color": "rgba(245,101,101,0.2)"},
                    ],
                    "threshold": {"line": {"color": "#f6ad55", "width": 4}, "thickness": 0.8, "value": fare},
                },
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#90adc4"),
                height=260,
                margin=dict(l=60, r=60, t=20, b=60),
            )
            st.plotly_chart(fig_gauge, width="stretch")
            st.markdown("""
            <div style="display:flex;justify-content:space-between;margin:-1.5rem 4rem 1rem 4rem;font-size:0.78rem;">
                <span style="color:#68d391;">🟢 Cheap</span>
                <span style="color:#f6ad55;">🟡 Moderate</span>
                <span style="color:#fc8181;">🔴 Expensive</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
            ch1, ch2 = st.columns(2)

            # Chart 1: Fare vs Days Before Departure
            with ch1:
                st.markdown('<div class="section-label">📈 Fare vs Booking Window</div>', unsafe_allow_html=True)
                day_points = [1, 3, 7, 14, 21, 30, 45, 60, 75, 90]
                fares_over_time = []
                for d in day_points:
                    p = {**payload, "days_before_departure": d}
                    try:
                        r = requests.post(f"{API_URL}/predict", json=p, timeout=3).json()
                        fares_over_time.append(r.get("predicted_fare_inr", fare))
                    except:
                        fares_over_time.append(fare)

                fig1 = go.Figure()
                fig1.add_trace(go.Scatter(
                    x=day_points, y=fares_over_time,
                    mode="lines+markers",
                    line=dict(color="#63b3ed", width=2.5),
                    marker=dict(size=7, color="#90cdf4"),
                    fill="tozeroy",
                    fillcolor="rgba(99,179,237,0.08)",
                    hovertemplate="Day %{x}: ₹%{y:,}<extra></extra>"
                ))
                fig1.add_vline(x=days_before, line_dash="dash", line_color="#f6ad55",
                               annotation_text=f"Today ({days_before}d)", annotation_font_color="#f6ad55")
                fig1.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#90adc4", size=11),
                    xaxis=dict(title="Days Before Departure", gridcolor="rgba(99,179,237,0.08)",
                               color="#4a6fa5", zeroline=False),
                    yaxis=dict(title="Fare (₹)", gridcolor="rgba(99,179,237,0.08)",
                               color="#4a6fa5", zeroline=False),
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=260,
                )
                st.plotly_chart(fig1, width='stretch')

            # Chart 2: Airline Fare Comparison
            with ch2:
                st.markdown('<div class="section-label">🏷️ Airline Fare Comparison</div>', unsafe_allow_html=True)
                airline_fares = {}
                for al in opts["airlines"]:
                    p = {**payload, "airline": al}
                    try:
                        r = requests.post(f"{API_URL}/predict", json=p, timeout=3).json()
                        airline_fares[al] = r.get("predicted_fare_inr", fare)
                    except:
                        airline_fares[al] = fare

                sorted_airlines = sorted(airline_fares, key=airline_fares.get)
                colors = ["#63b3ed" if a != airline else "#f6ad55" for a in sorted_airlines]

                fig2 = go.Figure(go.Bar(
                    x=[airline_fares[a] for a in sorted_airlines],
                    y=sorted_airlines,
                    orientation="h",
                    marker_color=colors,
                    hovertemplate="%{y}: ₹%{x:,}<extra></extra>",
                    text=[f"₹{airline_fares[a]:,}" for a in sorted_airlines],
                    textposition="outside",
                    textfont=dict(color="#90adc4", size=10),
                ))
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#90adc4", size=11),
                    xaxis=dict(gridcolor="rgba(99,179,237,0.08)", color="#4a6fa5", zeroline=False),
                    yaxis=dict(color="#4a6fa5"),
                    margin=dict(l=10, r=60, t=10, b=10),
                    height=260,
                )
                st.plotly_chart(fig2, width='stretch')

            # Chart 3: Economy vs Business across stops
            st.markdown('<div class="section-label">💺 Economy vs Business · All Stop Types</div>', unsafe_allow_html=True)
            stops_list = opts["stops"]
            eco_fares, biz_fares = [], []
            for s in stops_list:
                pe = {**payload, "stops": s, "class": "Economy"}
                pb = {**payload, "stops": s, "class": "Business"}
                try:
                    eco_fares.append(requests.post(f"{API_URL}/predict", json=pe, timeout=3).json().get("predicted_fare_inr", fare))
                    biz_fares.append(requests.post(f"{API_URL}/predict", json=pb, timeout=3).json().get("predicted_fare_inr", fare))
                except:
                    eco_fares.append(fare)
                    biz_fares.append(fare * 2.8)

            fig3 = go.Figure()
            fig3.add_trace(go.Bar(name="Economy", x=stops_list, y=eco_fares,
                                  marker_color="#63b3ed",
                                  hovertemplate="%{x} Economy: ₹%{y:,}<extra></extra>"))
            fig3.add_trace(go.Bar(name="Business", x=stops_list, y=biz_fares,
                                  marker_color="#f6ad55",
                                  hovertemplate="%{x} Business: ₹%{y:,}<extra></extra>"))
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#90adc4", size=11),
                barmode="group",
                xaxis=dict(gridcolor="rgba(99,179,237,0.08)", color="#4a6fa5"),
                yaxis=dict(title="Fare (₹)", gridcolor="rgba(99,179,237,0.08)", color="#4a6fa5", zeroline=False),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#90adc4")),
                margin=dict(l=10, r=10, t=10, b=10),
                height=240,
            )
            st.plotly_chart(fig3, width='stretch')

    except Exception:
        pass

# ─── Footer ───
st.markdown("""
<div class="footer">
    SkyFare · Gradient Boosting Regressor · R² 0.98 · Synthetic Indian Domestic Flight Data 2024<br>
    <span style="color:#2d4a6e;">Built with Streamlit · Flask · scikit-learn</span>
</div>
""", unsafe_allow_html=True)
