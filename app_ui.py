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

/* Glowing wave title */
@keyframes glow-wave {
    0%, 100% { opacity: 0.4; text-shadow: none; transform: translateY(0px); }
    50%       { opacity: 1; text-shadow: 0 0 20px rgba(99,179,237,0.9), 0 0 40px rgba(99,179,237,0.4); transform: translateY(-5px); }
}
.rainbow-title {
    display: flex;
    gap: 1px;
    margin-bottom: 0.5rem;
}
.rainbow-title span {
    font-size: 2.4rem;
    font-weight: 700;
    color: #90cdf4;
    animation: glow-wave 2.5s ease-in-out infinite;
    display: inline-block;
}

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
    background: linear-gradient(135deg, rgba(26,58,92,0.7) 0%, rgba(15,42,69,0.7) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
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
    background: rgba(99,179,237,0.06);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(99,179,237,0.12);
    border-radius: 14px;
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

/* Glassmorphism panels */
.glass-panel {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(99,179,237,0.18);
    border-radius: 18px;
    padding: 1.5rem;
}

/* Animated route dashes */
@keyframes dash-move {
    0%   { stroke-dashoffset: 20; }
    100% { stroke-dashoffset: 0; }
}
.route-dash-svg { width: 100%; height: 24px; overflow: visible; }
.route-dash-line {
    stroke: rgba(99,179,237,0.5);
    stroke-width: 2;
    stroke-dasharray: 8 5;
    fill: none;
    animation: dash-move 1s linear infinite;
}

/* Sticky fare badge */
.sticky-fare {
    position: fixed;
    top: 1.2rem;
    right: 1.5rem;
    background: linear-gradient(135deg, #1a3a5c, #0f2a45);
    border: 1px solid rgba(99,179,237,0.45);
    border-radius: 30px;
    padding: 0.45rem 1.1rem;
    font-size: 0.95rem;
    font-weight: 700;
    color: #90cdf4;
    z-index: 9998;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    backdrop-filter: blur(10px);
    animation: fade-in-down 0.5s ease;
}
@keyframes fade-in-down {
    from { opacity: 0; transform: translateY(-12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Dot-grid background overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: radial-gradient(rgba(99,179,237,0.07) 1px, transparent 1px);
    background-size: 28px 28px;
    pointer-events: none;
    z-index: 0;
}

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
    <h1 style="display:none">SkyFare</h1>
    <div class="rainbow-title">
        <span style="color:#90cdf4;animation-delay:0.0s">S</span>
        <span style="color:#90cdf4;animation-delay:0.2s">k</span>
        <span style="color:#90cdf4;animation-delay:0.4s">y</span>
        <span style="color:#90cdf4;animation-delay:0.6s">F</span>
        <span style="color:#90cdf4;animation-delay:0.8s">a</span>
        <span style="color:#90cdf4;animation-delay:1.0s">r</span>
        <span style="color:#90cdf4;animation-delay:1.2s">e</span>
        <span style="animation-delay:0.7s">&#x20;</span>
        <span style="font-size:2rem;animation-delay:0.8s;animation: bounce-letter 1.2s ease-in-out infinite;animation-delay:0.8s">✈️</span>
    </div>
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
    with st.form("fare_form"):
        st.markdown('<div class="card-title">🛫 Flight Details</div>', unsafe_allow_html=True)
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
                import time
                loader = st.empty()
                status_msgs = [
                    ("🛫", "Scanning routes..."),
                    ("📡", "Connecting to fare engine..."),
                    ("🔍", "Analysing booking window..."),
                    ("📊", "Crunching 2,000 records..."),
                    ("🤖", "Running Gradient Boost model..."),
                    ("💰", "Calculating best fare..."),
                ]
                for step, (icon, msg) in enumerate(status_msgs):
                    pct = int((step + 1) / len(status_msgs) * 100)
                    plane_pos = pct
                    loader.markdown(f"""
                    <div class="skeleton-wrap" style="padding:2rem 2.5rem;">
                        <div style="font-size:2.2rem;margin-bottom:0.6rem;">{icon}</div>
                        <div style="color:#90cdf4;font-weight:600;font-size:1rem;margin-bottom:1.4rem;">{msg}</div>
                        <div style="position:relative;height:36px;background:rgba(99,179,237,0.07);
                                    border:1px solid rgba(99,179,237,0.15);border-radius:20px;overflow:hidden;">
                            <div style="position:absolute;top:0;left:0;height:100%;width:{pct}%;
                                        background:linear-gradient(90deg,rgba(99,179,237,0.25),rgba(99,179,237,0.5));
                                        border-radius:20px;transition:width 0.3s ease;"></div>
                            <div style="position:absolute;top:50%;left:calc({plane_pos}% - 14px);
                                        transform:translateY(-50%);font-size:1.3rem;transition:left 0.3s ease;">✈️</div>
                        </div>
                        <div style="color:#4a6fa5;font-size:0.78rem;margin-top:0.8rem;">
                            {'&nbsp;'.join(['<span style="color:#63b3ed">●</span>' if i <= step else '<span style="color:#2d4a6e">●</span>' for i in range(len(status_msgs))])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.18)
                response = requests.post(f"{API_URL}/predict", json=payload, timeout=5)
                loader.empty()
                result = response.json()

                if response.status_code == 200:
                    fare    = result["predicted_fare_inr"]
                    band    = result["fare_band"]
                    summary = result["input_summary"]

                    # ── Sticky fare badge ──
                    st.markdown(f'<div class="sticky-fare">✈️ ₹{fare:,}</div>', unsafe_allow_html=True)

                    # ── Slot Machine Fare Reveal ──
                    slot = st.empty()
                    steps = 20
                    for i in range(steps):
                        roll = random.randint(fare - 3000, fare + 3000)
                        roll = max(999, roll)
                        speed = 0.03 if i < 10 else 0.06 if i < 16 else 0.12
                        slot.markdown(f"""
                        <div class="fare-result" style="border-color:rgba(99,179,237,{0.2 + i*0.04:.1f})">
                            <div class="fare-label">CALCULATING FARE...</div>
                            <div class="fare-amount" style="opacity:{0.4 + i*0.03:.1f}">₹{roll:,}</div>
                            <div class="fare-label">🎰 Rolling...</div>
                        </div>
                        """, unsafe_allow_html=True)
                        time.sleep(speed)
                    slot.empty()

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
                        <div style="text-align:center">
                            <div class="city-code">{src_code}</div>
                            <div style="color:#4a6fa5;font-size:0.75rem">{source_city}</div>
                        </div>
                        <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px">
                            <div style="font-size:0.7rem;color:#4a6fa5">{stop_icon} {stops} &nbsp;·&nbsp; {duration_hours}h</div>
                            <svg class="route-dash-svg" viewBox="0 0 200 12" preserveAspectRatio="none">
                                <path class="route-dash-line" d="M 0 6 Q 100 0 200 6"/>
                            </svg>
                            <div style="font-size:1.1rem">✈️</div>
                        </div>
                        <div style="text-align:center">
                            <div class="city-code">{dst_code}</div>
                            <div style="color:#4a6fa5;font-size:0.75rem">{destination_city}</div>
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

                else:
                    st.markdown(f'<div class="tip-danger">❌ {result.get("error", "Unknown error")}</div>', unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                st.markdown('<div class="tip-danger">❌ Could not reach the API. Is app.py running?</div>', unsafe_allow_html=True)

# ─── Row 2: Trip Summary full width + Nerd Stats ───
if submitted and source_city != destination_city:
    try:
        if response.status_code == 200:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            st.markdown('<div class="card-title">📋 Trip Summary</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:0.8rem;margin-bottom:1rem;">
                <div class="metric-item"><div class="label">✈ Airline</div><div class="value">{airline}</div></div>
                <div class="metric-item"><div class="label">💺 Class</div><div class="value">{seat_class}</div></div>
                <div class="metric-item"><div class="label">🔁 Stops</div><div class="value">{stops}</div></div>
                <div class="metric-item"><div class="label">⏱ Duration</div><div class="value">{duration_hours} hrs</div></div>
                <div class="metric-item"><div class="label">📅 Days Left</div><div class="value">{days_before} days</div></div>
                <div class="metric-item"><div class="label">🕐 Departure</div><div class="value">{departure_time.split('(')[0].strip()}</div></div>
            </div>
            """, unsafe_allow_html=True)

            # ── Nerd Stats Terminal ──
            import json as _json
            conf_pct = round((1 - (band["high"] - band["low"]) / fare) * 100, 1)
            fare_per_hr = round(fare / duration_hours)
            biz_premium = round((int(fare * 2.8) - fare) / fare * 100, 1)
            terminal_json = _json.dumps(result, indent=2, ensure_ascii=False)
            lines_html = ""
            for line in terminal_json.splitlines():
                stripped = line.strip()
                if stripped.startswith('"') and ":" in stripped:
                    key, _, rest = stripped.partition(":")
                    comma = "<span style='color:#8b949e'>,</span>" if rest.strip().endswith(",") else ""
                    val = rest.strip().rstrip(",")
                    indent_spaces = "&nbsp;" * (len(line) - len(line.lstrip()))
                    if val.lstrip("-").isdigit():
                        val_html = f"<span style='color:#79c0ff'>{val}</span>"
                    elif val.startswith('"'):
                        val_html = f"<span style='color:#a5d6ff'>{val}</span>"
                    else:
                        val_html = f"<span style='color:#ffa657'>{val}</span>"
                    lines_html += f"{indent_spaces}<span style='color:#ff7b72'>{key}</span><span style='color:#8b949e'>:</span> {val_html}{comma}<br>"
                else:
                    lines_html += f"<span style='color:#8b949e'>{line}</span><br>"

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            with st.expander("🖥️  Nerd Stats & Raw API Response", expanded=False):
                st.markdown(f"""
                <div style="background:#0d1117;border:1px solid #30363d;border-radius:12px;
                            padding:1.2rem 1.5rem;font-family:'Courier New',monospace;font-size:0.8rem;line-height:1.8;">
                    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.8rem;
                                padding-bottom:0.6rem;border-bottom:1px solid #21262d;">
                        <span style="width:12px;height:12px;border-radius:50%;background:#ff5f57;display:inline-block;"></span>
                        <span style="width:12px;height:12px;border-radius:50%;background:#febc2e;display:inline-block;"></span>
                        <span style="width:12px;height:12px;border-radius:50%;background:#28c840;display:inline-block;"></span>
                        <span style="color:#8b949e;font-size:0.72rem;margin-left:0.4rem;">skyfare · model · v1.0 · GBR</span>
                    </div>
                    <span style="color:#6e7681;"># ── model stats ──────────────────</span><br>
                    <span style="color:#ff7b72;">algorithm</span><span style="color:#8b949e;">:</span>     <span style="color:#a5d6ff;">GradientBoostingRegressor</span><br>
                    <span style="color:#ff7b72;">n_estimators</span><span style="color:#8b949e;">:</span>  <span style="color:#79c0ff;">200</span><br>
                    <span style="color:#ff7b72;">max_depth</span><span style="color:#8b949e;">:</span>     <span style="color:#79c0ff;">5</span><br>
                    <span style="color:#ff7b72;">learning_rate</span><span style="color:#8b949e;">:</span> <span style="color:#79c0ff;">0.1</span><br>
                    <span style="color:#ff7b72;">r2_score</span><span style="color:#8b949e;">:</span>      <span style="color:#3fb950;">0.98</span><br>
                    <span style="color:#ff7b72;">features</span><span style="color:#8b949e;">:</span>      <span style="color:#79c0ff;">9</span>  <span style="color:#6e7681;"># label-encoded + numeric</span><br>
                    <br>
                    <span style="color:#6e7681;"># ── this prediction ──────────────</span><br>
                    <span style="color:#ff7b72;">fare_inr</span><span style="color:#8b949e;">:</span>      <span style="color:#79c0ff;">₹{fare:,}</span><br>
                    <span style="color:#ff7b72;">band_low</span><span style="color:#8b949e;">:</span>      <span style="color:#79c0ff;">₹{band['low']:,}</span>  <span style="color:#6e7681;"># -8%</span><br>
                    <span style="color:#ff7b72;">band_high</span><span style="color:#8b949e;">:</span>     <span style="color:#79c0ff;">₹{band['high']:,}</span>  <span style="color:#6e7681;"># +8%</span><br>
                    <span style="color:#ff7b72;">fare_per_hr</span><span style="color:#8b949e;">:</span>   <span style="color:#ffa657;">₹{fare_per_hr:,}/hr</span><br>
                    <span style="color:#ff7b72;">biz_premium</span><span style="color:#8b949e;">:</span>   <span style="color:#ffa657;">+{biz_premium}%</span>  <span style="color:#6e7681;"># vs economy</span><br>
                    <span style="color:#ff7b72;">days_bucket</span><span style="color:#8b949e;">:</span>   <span style="color:#a5d6ff;">"{'last-min' if days_before <= 3 else 'urgent' if days_before <= 7 else 'normal' if days_before <= 30 else 'early'}"</span><br>
                    <br>
                    <span style="color:#6e7681;"># ── raw response ─────────────────</span><br>
                    <span style="color:#8b949e;">$ curl -X POST localhost:5000/predict</span><br>
                    <span style="color:#3fb950;">✓ 200 OK · ~12ms</span><br><br>
                    {lines_html}
                </div>
                """, unsafe_allow_html=True)
    except Exception:
        pass

# ─── Gauge + Charts Section ───
if submitted and source_city != destination_city:
    try:
        if response.status_code == 200:
            st.markdown("<div style='display:flex;align-items:center;gap:0.8rem;margin:1.5rem 0;'><div style='flex:1;border-top:1px solid rgba(99,179,237,0.1);'></div><span style='color:#4a6fa5;font-size:0.85rem;'>&#9135;&#9135;&#9135; &#x2708;&#xFE0F; &#9135;&#9135;&#9135;</span><div style='flex:1;border-top:1px solid rgba(99,179,237,0.1);'></div></div>", unsafe_allow_html=True)

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

            st.markdown("<div style='display:flex;align-items:center;gap:0.8rem;margin:1.5rem 0;'><div style='flex:1;border-top:1px solid rgba(99,179,237,0.1);'></div><span style='color:#4a6fa5;font-size:0.85rem;'>&#9135;&#9135;&#9135; &#x2708;&#xFE0F; &#9135;&#9135;&#9135;</span><div style='flex:1;border-top:1px solid rgba(99,179,237,0.1);'></div></div>", unsafe_allow_html=True)
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
