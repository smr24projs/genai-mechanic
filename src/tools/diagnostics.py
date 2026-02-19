import pandas as pd
import json
from catboost import CatBoostClassifier
from langchain.tools import tool

# Load the REALISTIC model
try:
    ml_model = CatBoostClassifier()
    ml_model.load_model("mechanic_catboost_realistic.cbm")
except Exception as e:
    ml_model = None

@tool
def predict_vehicle_fault(
    car_model: str, year: float, engine_rpm: float, vehicle_speed: float, 
    engine_load: float, coolant_temp: float, maf_grams_sec: float, 
    short_term_trim: float, long_term_trim: float, throttle_pos: float
) -> str:
    """Predicts DTC and returns Confidence Score. Input live sensor data."""
    if ml_model is None: return json.dumps({"prediction": "ERROR", "confidence": 0.0})

    input_data = pd.DataFrame([{
        'CAR_MODEL': car_model, 'YEAR': year, 'ENGINE_RPM': engine_rpm,
        'VEHICLE_SPEED': vehicle_speed, 'ENGINE_LOAD': engine_load,
        'COOLANT_TEMP': coolant_temp, 'MAF_GRAMS_SEC': maf_grams_sec,
        'SHORT_TERM_TRIM': short_term_trim, 'LONG_TERM_TRIM': long_term_trim,
        'THROTTLE_POS': throttle_pos
    }])

    # Get Prediction & Confidence
    prediction = ml_model.predict(input_data)[0][0]
    probabilities = ml_model.predict_proba(input_data)[0]
    confidence_score = float(max(probabilities) * 100)
    
    # Return as a JSON string so LangGraph can easily parse it
    return json.dumps({
        "prediction": prediction,
        "confidence": confidence_score
    })

def get_ml_diagnostic_tool():
    return predict_vehicle_fault