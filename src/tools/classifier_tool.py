import joblib
import numpy as np
import json
import re as _re
from langchain.tools import tool

# --- Car model keyword map ---
_MODEL_MAP = {
    "nexon": "Tata Nexon", "harrier": "Tata Harrier", "safari": "Tata Safari",
    "altroz": "Tata Altroz", "punch": "Tata Punch", "swift": "Maruti Swift",
    "vitara": "Maruti Suzuki Vitara Brezza", "brezza": "Maruti Suzuki Vitara Brezza",
    "baleno": "Maruti Baleno", "creta": "Hyundai Creta", "i20": "Hyundai i20",
    "venue": "Hyundai Venue", "xuv700": "Mahindra XUV700", "xuv500": "Mahindra XUV500",
    "scorpio": "Mahindra Scorpio", "civic": "Honda Civic", "city": "Honda City",
    "fortuner": "Toyota Fortuner", "innova": "Toyota Innova",
    "f-150": "Ford F-150", "ecosport": "Ford EcoSport", "ecoboost": "Ford EcoSport",
    "xuv": "Mahindra XUV500", "kwid": "Renault Kwid", "duster": "Renault Duster",
}

class VehicleClassifier:
    def __init__(self):
        self.model = joblib.load('models/dtc_classifier.pkl')
        self.model_enc = joblib.load('models/car_model_encoder.pkl')
        self.label_enc = joblib.load('models/target_label_encoder.pkl')

    def predict(self, sensor_data: dict):
        """
        sensor_data keys: CAR_MODEL, YEAR, ENGINE_RPM, VEHICLE_SPEED,
        ENGINE_LOAD, COOLANT_TEMP, MAF_GRAMS_SEC, SHORT_TERM_TRIM,
        LONG_TERM_TRIM, THROTTLE_POS
        """
        try:
            model_val = self.model_enc.transform([sensor_data.get('CAR_MODEL', 'Tata Nexon')])[0]
        except ValueError:
            model_val = 0

        features = [
            model_val,
            float(sensor_data.get('YEAR', 2020)),
            float(sensor_data.get('ENGINE_RPM', 1500)),
            float(sensor_data.get('VEHICLE_SPEED', 30)),
            float(sensor_data.get('ENGINE_LOAD', 35)),
            float(sensor_data.get('COOLANT_TEMP', 88)),
            float(sensor_data.get('MAF_GRAMS_SEC', 10)),
            float(sensor_data.get('SHORT_TERM_TRIM', 0)),
            float(sensor_data.get('LONG_TERM_TRIM', 0)),
            float(sensor_data.get('THROTTLE_POS', 20))
        ]

        probs = self.model.predict_proba([features])[0]
        max_prob = np.max(probs)
        prediction_idx = np.argmax(probs)
        dtc_code = self.label_enc.inverse_transform([prediction_idx])[0]

        # Also return top-3 predictions for richer context
        top3_idx = np.argsort(probs)[-3:][::-1]
        top3 = [
            {"dtc": self.label_enc.inverse_transform([i])[0], "prob": round(float(probs[i]), 3)}
            for i in top3_idx
        ]

        return {
            "status": "CONFIDENT" if max_prob >= 0.70 else "UNCERTAIN",
            "confidence": round(float(max_prob), 4),
            "prediction": dtc_code,
            "top3_predictions": top3,
            "action": "Immediate diagnosis identified." if max_prob >= 0.70 else "Triggering deeper RAG and Web Research."
        }


def _parse_sensor_data(query: str) -> tuple:
    """
    Robustly parses sensor values from the agent's natural language query.
    Returns (sensor_data dict, count of fields extracted from query).
    """
    sensor_data = {
        "CAR_MODEL": None, "YEAR": 2020,
        "ENGINE_RPM": None, "VEHICLE_SPEED": None, "ENGINE_LOAD": None,
        "COOLANT_TEMP": None, "MAF_GRAMS_SEC": 10,
        "SHORT_TERM_TRIM": None, "LONG_TERM_TRIM": None, "THROTTLE_POS": None
    }
    extracted = 0
    lower_q = query.lower()

    # --- 1. Try JSON parse first (agent may pass structured JSON) ---
    try:
        stripped = query.strip()
        if stripped.startswith("{"):
            parsed = json.loads(stripped)
            mapping = {
                "rpm": "ENGINE_RPM", "ENGINE_RPM": "ENGINE_RPM",
                "speed": "VEHICLE_SPEED", "VEHICLE_SPEED": "VEHICLE_SPEED",
                "load": "ENGINE_LOAD", "ENGINE_LOAD": "ENGINE_LOAD",
                "temp": "COOLANT_TEMP", "COOLANT_TEMP": "COOLANT_TEMP",
                "model": "CAR_MODEL", "CAR_MODEL": "CAR_MODEL", "year": "YEAR",
                "short_term_trim": "SHORT_TERM_TRIM", "long_term_trim": "LONG_TERM_TRIM",
                "throttle": "THROTTLE_POS",
            }
            for k, v in parsed.items():
                key = mapping.get(k)
                if key:
                    sensor_data[key] = v
                    extracted += 1
            # Skip regex if we got JSON
            if extracted >= 3:
                _fill_defaults(sensor_data)
                return sensor_data, extracted
    except Exception:
        pass

    # --- 2. Car model keyword match ---
    for keyword, model_name in _MODEL_MAP.items():
        if keyword in lower_q:
            sensor_data["CAR_MODEL"] = model_name
            extracted += 1
            break

    # --- 3. Year (2000–2025) ---
    year_m = _re.search(r'\b(20[0-2][0-9])\b', query)
    if year_m:
        sensor_data["YEAR"] = int(year_m.group(1))

    # --- 4. RPM ---
    rpm_m = _re.search(r'rpm[=:\s]+([0-9]+)|([0-9]+)\s*rpm', lower_q)
    if rpm_m and sensor_data["ENGINE_RPM"] is None:
        sensor_data["ENGINE_RPM"] = float(rpm_m.group(1) or rpm_m.group(2))
        extracted += 1

    # --- 5. Speed ---
    spd_m = _re.search(r'speed[=:\s]+([0-9]+)|([0-9]+)\s*km(?:/h)?', lower_q)
    if spd_m and sensor_data["VEHICLE_SPEED"] is None:
        sensor_data["VEHICLE_SPEED"] = float(spd_m.group(1) or spd_m.group(2))
        extracted += 1

    # --- 6. Engine Load ---
    load_m = _re.search(r'load[=:\s]+([0-9]+)|([0-9]+)\s*%\s*load|engine\s+load[=:\s]+([0-9]+)', lower_q)
    if load_m and sensor_data["ENGINE_LOAD"] is None:
        val = load_m.group(1) or load_m.group(2) or load_m.group(3)
        if val:
            sensor_data["ENGINE_LOAD"] = float(val)
            extracted += 1

    # --- 7. Temperature ---
    tmp_m = _re.search(r'temp[=:\s]+([0-9]+)|coolant[=:\s]+([0-9]+)|([0-9]{2,3})\s*[°]?c\b', lower_q)
    if tmp_m and sensor_data["COOLANT_TEMP"] is None:
        val = tmp_m.group(1) or tmp_m.group(2) or tmp_m.group(3)
        if val:
            sensor_data["COOLANT_TEMP"] = float(val)
            extracted += 1

    # --- 8. Short-term fuel trim ---
    st_m = _re.search(r'short[\s_-]*term[\s_-]*(?:fuel[\s_-]*)?trim[s]?[=:\s]+(-?[0-9.]+)', lower_q)
    if st_m and sensor_data["SHORT_TERM_TRIM"] is None:
        sensor_data["SHORT_TERM_TRIM"] = float(st_m.group(1))
        extracted += 1

    # --- 9. Long-term fuel trim ---
    lt_m = _re.search(r'long[\s_-]*term[\s_-]*(?:fuel[\s_-]*)?trim[s]?[=:\s]+(-?[0-9.]+)', lower_q)
    if lt_m and sensor_data["LONG_TERM_TRIM"] is None:
        sensor_data["LONG_TERM_TRIM"] = float(lt_m.group(1))
        extracted += 1

    # --- 10. Throttle position ---
    thr_m = _re.search(r'throttle[=:\s]+([0-9]+)', lower_q)
    if thr_m and sensor_data["THROTTLE_POS"] is None:
        sensor_data["THROTTLE_POS"] = float(thr_m.group(1))
        extracted += 1

    _fill_defaults(sensor_data)
    return sensor_data, extracted


def _fill_defaults(sensor_data: dict):
    """Fill any remaining None values with safe neutral defaults."""
    defaults = {
        "CAR_MODEL": "Tata Nexon", "ENGINE_RPM": 1500, "VEHICLE_SPEED": 30,
        "ENGINE_LOAD": 35, "COOLANT_TEMP": 88, "SHORT_TERM_TRIM": 0,
        "LONG_TERM_TRIM": 0, "THROTTLE_POS": 20
    }
    for key, dval in defaults.items():
        if sensor_data.get(key) is None:
            sensor_data[key] = dval


# --- TOOL DEFINITION ---
@tool
def predict_root_cause(query: str):
    """
    Predicts the vehicle's most likely fault DTC code using a Random Forest ML model trained on OBD-II sensor data.
    Include RPM, Speed, Load%, Temp°C, and vehicle model in your query for best accuracy.
    Returns JSON with confidence score, predicted DTC, top-3 predictions, and ml_score_hint.

    CRITICAL: Always use the 'ml_score_hint' integer (0-100) directly as the ml_score in your final response JSON.
    If data_quality is 'LOW', reduce the ml_score by 15 points to reflect uncertainty from missing sensor data.
    """
    try:
        sensor_data, fields_extracted = _parse_sensor_data(query)

        classifier = VehicleClassifier()
        result = classifier.predict(sensor_data)

        # Metadata for grounding the LLM's score assignment
        result["fields_extracted"] = fields_extracted
        result["data_quality"] = (
            "HIGH" if fields_extracted >= 5 else
            "MEDIUM" if fields_extracted >= 3 else
            "LOW — sensor defaults used, reduce ml_score by 15 points"
        )
        result["parsed_sensors"] = {
            "model": sensor_data["CAR_MODEL"],
            "rpm": sensor_data["ENGINE_RPM"],
            "speed": sensor_data["VEHICLE_SPEED"],
            "load_pct": sensor_data["ENGINE_LOAD"],
            "temp_c": sensor_data["COOLANT_TEMP"],
        }
        # Direct instruction to the LLM: use this number
        base_score = round(result["confidence"] * 100)
        penalty = 15 if fields_extracted < 3 else (5 if fields_extracted < 5 else 0)
        result["ml_score_hint"] = max(0, base_score - penalty)

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": str(e), "ml_score_hint": 0})
