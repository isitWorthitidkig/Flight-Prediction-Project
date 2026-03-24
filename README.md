# ✈️ Flight Fare Prediction Project

A machine learning project that predicts domestic flight fares across major Indian cities using a **Gradient Boosting Regressor**.

## 🔍 Overview

| | Original Project | This Project |
|---|---|---|
| **Domain** | Tech salaries | Indian domestic flights |
| **Dataset** | 2,000 employee records | 2,000 booking records |
| **Model** | Gradient Boosting | Gradient Boosting |
| **Features** | 6 features | 9 features |
| **Target** | Annual salary (USD) | Flight fare (INR) |
| **API** | Flask | Flask |
| **UI** | Streamlit | Streamlit with booking tips & fare band |

---

## 📁 Project Structure

```
flight_fare_prediction/
│
├── train_model.py        # Generate dataset & train model
├── app.py                # Flask REST API
├── app_ui.py             # Streamlit frontend
├── requirements.txt      # Python dependencies
├── flight_data.csv       # Generated after training (2,000 rows)
├── model.pkl             # Saved Gradient Boosting model
├── encoders.pkl          # Label encoders for categorical features
└── feature_columns.pkl   # Feature column order
```

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the model
```bash
python train_model.py
```
This will:
- Generate `flight_data.csv` (2,000 synthetic booking records)
- Train a Gradient Boosting Regressor
- Save `model.pkl`, `encoders.pkl`, `feature_columns.pkl`
- Print MAE and R² scores

### 3. Run the Flask API
```bash
python app.py
```
API runs at `http://localhost:5000`

### 4. Run the Streamlit UI
```bash
streamlit run app_ui.py
```
UI opens at `http://localhost:8501`

---

## 🌐 API Reference

### `GET /`
Returns API status.

### `GET /options`
Returns valid values for all categorical inputs.

### `POST /predict`

**Request body:**
```json
{
    "airline": "IndiGo",
    "source_city": "Delhi",
    "destination_city": "Mumbai",
    "departure_time": "Morning (06-12)",
    "arrival_time": "Afternoon (12-18)",
    "stops": "non-stop",
    "class": "Economy",
    "days_before_departure": 15,
    "duration_hours": 2.2
}
```

**Response:**
```json
{
    "predicted_fare_inr": 7450,
    "formatted": "₹7,450",
    "fare_band": { "low": 6854, "high": 8046 },
    "input_summary": { ... }
}
```

---

## 📊 Features Used

| Feature | Type | Description |
|---|---|---|
| `airline` | Categorical | 6 Indian airlines |
| `source_city` | Categorical | 10 major cities |
| `destination_city` | Categorical | 10 major cities |
| `departure_time` | Categorical | 5 time-of-day slots |
| `arrival_time` | Categorical | 5 time-of-day slots |
| `stops` | Categorical | non-stop / 1 stop / 2+ stops |
| `class` | Categorical | Economy / Business |
| `days_before_departure` | Numeric | 1–90 days |
| `duration_hours` | Numeric | 0.5–12 hours |

---

## 🤖 Model Details

- **Algorithm:** Gradient Boosting Regressor (`sklearn`)
- **Estimators:** 200
- **Max Depth:** 5
- **Learning Rate:** 0.1
- **Typical MAE:** ~₹400–600
- **Typical R²:** ~0.93–0.96

---

## 💡 Key Features

1. **9 input features** — airline, route, time slots, stops, class, booking window, duration
2. **Booking tip** — UI advises whether you're booking early, on time, or last-minute
3. **Fare band** — ±8% confidence range shown in UI
4. **Input validation** — same-city routes blocked, numeric ranges enforced
5. **India-focused** — covers 10 major domestic routes, 6 real airlines
