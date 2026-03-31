"""
Flight Fare Prediction - Model Training Script
Dataset: Synthetic Indian Domestic Flight Data (2024)
Features: airline, source_city, destination_city, departure_time, arrival_time,
          stops, class, days_before_departure, duration_hours
Target: fare_inr
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score

# ─────────────────────────────────────────────
# 1. Generate Synthetic Dataset
# ─────────────────────────────────────────────
np.random.seed(42)
N = 2000

airlines = ["IndiGo", "Air India", "SpiceJet", "Vistara", "GoFirst", "AirAsia India"]

cities = ["Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai",
          "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Goa"]

time_slots = ["Early Morning (00-06)", "Morning (06-12)",
              "Afternoon (12-18)", "Evening (18-21)", "Night (21-00)"]

stops_options = ["non-stop", "1 stop", "2+ stops"]

seat_class = ["Economy", "Business"]

# Route distances (approx km) between city pairs - affects duration & base fare
route_distance = {
    ("Delhi", "Mumbai"): 1400, ("Delhi", "Bangalore"): 1740, ("Delhi", "Chennai"): 1770,
    ("Delhi", "Hyderabad"): 1250, ("Delhi", "Kolkata"): 1300, ("Delhi", "Goa"): 1900,
    ("Delhi", "Pune"): 1400, ("Delhi", "Ahmedabad"): 900, ("Delhi", "Jaipur"): 270,
    ("Mumbai", "Bangalore"): 980, ("Mumbai", "Chennai"): 1330, ("Mumbai", "Kolkata"): 1660,
    ("Mumbai", "Hyderabad"): 710, ("Mumbai", "Goa"): 600, ("Mumbai", "Jaipur"): 1150,
    ("Mumbai", "Ahmedabad"): 530, ("Mumbai", "Pune"): 150,
    ("Bangalore", "Chennai"): 330, ("Bangalore", "Hyderabad"): 570, ("Bangalore", "Kolkata"): 1870,
    ("Bangalore", "Goa"): 570, ("Bangalore", "Pune"): 840, ("Bangalore", "Ahmedabad"): 1500,
    ("Bangalore", "Jaipur"): 1900,
    ("Chennai", "Kolkata"): 1370, ("Chennai", "Hyderabad"): 630, ("Chennai", "Goa"): 920,
    ("Chennai", "Pune"): 1150, ("Chennai", "Ahmedabad"): 1650, ("Chennai", "Jaipur"): 1900,
    ("Hyderabad", "Kolkata"): 1490, ("Hyderabad", "Goa"): 650, ("Hyderabad", "Pune"): 560,
    ("Hyderabad", "Ahmedabad"): 1100, ("Hyderabad", "Jaipur"): 1200,
    ("Kolkata", "Goa"): 2100, ("Kolkata", "Pune"): 1650, ("Kolkata", "Ahmedabad"): 1950,
    ("Kolkata", "Jaipur"): 1500,
    ("Pune", "Goa"): 460, ("Pune", "Ahmedabad"): 660, ("Pune", "Jaipur"): 1150,
    ("Ahmedabad", "Jaipur"): 670, ("Ahmedabad", "Goa"): 1100,
    ("Jaipur", "Goa"): 1400,
}

airline_base_fare = {
    "IndiGo": 3500, "SpiceJet": 3200, "GoFirst": 3300,
    "AirAsia India": 3000, "Vistara": 5500, "Air India": 5000,
}

stops_multiplier = {"non-stop": 1.15, "1 stop": 1.0, "2+ stops": 0.85}
class_multiplier = {"Economy": 1.0, "Business": 2.8}

time_demand = {
    "Early Morning (00-06)": 0.85,
    "Morning (06-12)":       1.20,
    "Afternoon (12-18)":     1.00,
    "Evening (18-21)":       1.15,
    "Night (21-00)":         0.95,
}

# Arrival time also affects fare — late-night arrivals are less desirable = cheaper
arrival_demand = {
    "Early Morning (00-06)": 0.88,
    "Morning (06-12)":       1.10,
    "Afternoon (12-18)":     1.05,
    "Evening (18-21)":       1.08,
    "Night (21-00)":         0.92,
}

dep_hours_map = [3, 9, 15, 19, 22]  # representative hour for each time slot
stop_extra_map = {"non-stop": 0, "1 stop": 1, "2+ stops": 3}

rows = []
for _ in range(N):
    airline     = np.random.choice(airlines)
    src         = np.random.choice(cities)
    dst         = np.random.choice([c for c in cities if c != src])
    dep_time    = np.random.choice(time_slots)
    stops       = np.random.choice(stops_options, p=[0.45, 0.42, 0.13])
    cls         = np.random.choice(seat_class, p=[0.82, 0.18])
    days_before = int(np.random.choice(range(1, 91)))

    # Duration based on distance
    key  = tuple(sorted([src, dst]))
    dist = route_distance.get(key, 1000)
    base_duration  = dist / 700  # ~700 km/h cruise speed
    stop_extra     = {"non-stop": 0, "1 stop": 1.5, "2+ stops": 3.0}[stops]
    duration_hours = round(base_duration + stop_extra + np.random.normal(0, 0.2), 1)
    duration_hours = max(0.8, duration_hours)

    # Derive arrival time logically from departure + duration
    dep_hour       = dep_hours_map[time_slots.index(dep_time)]
    arr_hour       = (dep_hour + int(base_duration) + stop_extra_map[stops]) % 24
    arr_slot_index = min(range(len(dep_hours_map)), key=lambda i: abs(dep_hours_map[i] - arr_hour))
    arr_time       = time_slots[arr_slot_index]

    # Booking surge: last-minute & very early bookings differ
    if days_before <= 3:
        booking_factor = 1.45
    elif days_before <= 7:
        booking_factor = 1.25
    elif days_before <= 14:
        booking_factor = 1.10
    elif days_before >= 60:
        booking_factor = 0.90
    else:
        booking_factor = 1.0

    fare = (
        airline_base_fare[airline]
        + dist * 1.8
        * stops_multiplier[stops]
        * class_multiplier[cls]
        * time_demand[dep_time]
        * arrival_demand[arr_time]
        * booking_factor
        + np.random.normal(0, 200)          # reduced noise for cleaner signal
    )
    fare = max(999, int(fare))

    rows.append({
        "airline":              airline,
        "source_city":          src,
        "destination_city":     dst,
        "departure_time":       dep_time,
        "arrival_time":         arr_time,
        "stops":                stops,
        "class":                cls,
        "days_before_departure": days_before,
        "duration_hours":       duration_hours,
        "fare_inr":             fare,
    })

df = pd.DataFrame(rows)
df.to_csv("flight_data.csv", index=False)
print(f"✅ Dataset created: {df.shape[0]} rows × {df.shape[1]} columns")
print(df.describe())

# ─────────────────────────────────────────────
# 2. Preprocessing
# ─────────────────────────────────────────────
label_encoders = {}
cat_cols = ["airline", "source_city", "destination_city",
            "departure_time", "arrival_time", "stops", "class"]

df_enc = df.copy()
for col in cat_cols:
    le = LabelEncoder()
    df_enc[col] = le.fit_transform(df[col])
    label_encoders[col] = le

X = df_enc.drop("fare_inr", axis=1)
y = df_enc["fare_inr"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ─────────────────────────────────────────────
# 3. Train Model
# ─────────────────────────────────────────────
model = GradientBoostingRegressor(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)
model.fit(X_train, y_train)

# ─────────────────────────────────────────────
# 4. Evaluate
# ─────────────────────────────────────────────
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2  = r2_score(y_test, y_pred)

print(f"\n📊 Model Evaluation:")
print(f"   MAE  : ₹{mae:,.0f}")
print(f"   R²   : {r2:.4f}")

# ─────────────────────────────────────────────
# 5. Save Artifacts
# ─────────────────────────────────────────────
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("encoders.pkl", "wb") as f:
    pickle.dump(label_encoders, f)

with open("feature_columns.pkl", "wb") as f:
    pickle.dump(list(X.columns), f)

print("\n✅ Saved: model.pkl, encoders.pkl, feature_columns.pkl")
