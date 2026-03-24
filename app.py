"""
Flight Fare Prediction - Flask REST API
Endpoint: POST /predict
"""

from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Load model artifacts
model           = pickle.load(open("model.pkl", "rb"))
encoders        = pickle.load(open("encoders.pkl", "rb"))
feature_columns = pickle.load(open("feature_columns.pkl", "rb"))

OPTIONS = {
    "airlines": ["IndiGo", "Air India", "SpiceJet", "Vistara", "GoFirst", "AirAsia India"],
    "cities": ["Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai",
               "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Goa"],
    "time_slots": ["Early Morning (00-06)", "Morning (06-12)",
                   "Afternoon (12-18)", "Evening (18-21)", "Night (21-00)"],
    "stops": ["non-stop", "1 stop", "2+ stops"],
    "classes": ["Economy", "Business"],
}


@app.route("/")
def home():
    return jsonify({
        "message": "Flight Fare Prediction API is running ✈️",
        "endpoints": {
            "POST /predict": "Predict flight fare",
            "GET /options":  "Get valid input options"
        }
    })


@app.route("/options", methods=["GET"])
def get_options():
    return jsonify(OPTIONS)


@app.route("/predict", methods=["POST"])
def predict():
    """
    Expected JSON body:
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
    """
    try:
        data = request.json

        required = ["airline", "source_city", "destination_city", "departure_time",
                    "arrival_time", "stops", "class", "days_before_departure", "duration_hours"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400

        if data["source_city"] == data["destination_city"]:
            return jsonify({"error": "source_city and destination_city cannot be the same"}), 400

        # Validate & encode categoricals
        cat_cols = ["airline", "source_city", "destination_city",
                    "departure_time", "arrival_time", "stops", "class"]
        encoded = {}
        for col in cat_cols:
            le  = encoders[col]
            val = data[col]
            if val not in le.classes_:
                return jsonify({
                    "error": f"Invalid value for '{col}': '{val}'",
                    "valid_values": list(le.classes_)
                }), 400
            encoded[col] = int(le.transform([val])[0])

        # Validate numerics
        days = int(data["days_before_departure"])
        dur  = float(data["duration_hours"])
        if not (1 <= days <= 90):
            return jsonify({"error": "days_before_departure must be 1–90"}), 400
        if not (0.5 <= dur <= 12):
            return jsonify({"error": "duration_hours must be 0.5–12"}), 400

        feature_vector = [
            encoded["airline"],
            encoded["source_city"],
            encoded["destination_city"],
            encoded["departure_time"],
            encoded["arrival_time"],
            encoded["stops"],
            encoded["class"],
            days,
            dur,
        ]

        prediction = int(model.predict([feature_vector])[0])
        prediction = max(999, prediction)

        return jsonify({
            "predicted_fare_inr": prediction,
            "formatted":          f"₹{prediction:,}",
            "fare_band": {
                "low":  int(prediction * 0.92),
                "high": int(prediction * 1.08),
            },
            "input_summary": {
                "airline":               data["airline"],
                "route":                 f"{data['source_city']} → {data['destination_city']}",
                "departure_time":        data["departure_time"],
                "arrival_time":          data["arrival_time"],
                "stops":                 data["stops"],
                "class":                 data["class"],
                "days_before_departure": days,
                "duration_hours":        dur,
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
