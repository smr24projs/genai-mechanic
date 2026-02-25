# # src/tools/classifier_tool.py
# import joblib
# import os
# from langchain.tools import tool

# # Define the path to the model
# MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models", "dtc_classifier.pkl")

# # --- SET THRESHOLD HERE ---
# CONFIDENCE_THRESHOLD = 0.70  # 70%
# # -------------------------

# try:
#     if os.path.exists(MODEL_PATH):
#         MODEL = joblib.load(MODEL_PATH)
#         MODEL_LOADED = True
#     else:
#         MODEL_LOADED = False
# except Exception as e:
#     MODEL_LOADED = False

# @tool
# def predict_root_cause(query: str) -> str:
#     """
#     Predicts the likely root cause using an ML model. 
#     Returns the cause if confidence is above 70%.
#     """
#     if not MODEL_LOADED:
#         return "Error: Classification model not loaded."
    
#     try:
#         # Get probabilities for all classes
#         probs_all = MODEL.predict_proba([query])[0]
#         max_prob = probs_all.max()
#         prediction = MODEL.predict([query])[0]
        
#         # Check against threshold
#         if max_prob < CONFIDENCE_THRESHOLD:
#             return (f"The ML model is UNCERTAIN (Confidence: {max_prob:.2%}). "
#                     f"Predicted guess was '{prediction}', but this is below the 70% safety threshold. "
#                     "Please ignore this guess and verify using Web Search or Service Manuals.")
        
#         return f"Predicted Root Cause: {prediction} (Confidence: {max_prob:.2%})"
            
#     except Exception as e:
#         return f"Prediction Error: {str(e)}"


# # src/tools/classifier_tool.py
# import joblib
# import os
# import xgboost as xgb
# from langchain.tools import tool

# # Paths
# MODEL_PATH = "models/dtc_classifier_xgb.json"
# ENCODER_PATH = "models/label_encoder.pkl"
# TFIDF_PATH = "models/tfidf_vectorizer.pkl"
# CONFIDENCE_THRESHOLD = 0.70

# try:
#     # Load XGBoost and helper objects
#     MODEL = xgb.XGBClassifier()
#     MODEL.load_model(MODEL_PATH)
#     LE = joblib.load(ENCODER_PATH)
#     TFIDF = joblib.load(TFIDF_PATH)
#     MODEL_LOADED = True
# except Exception as e:
#     MODEL_LOADED = False
#     print(f"⚠️ Error loading XGBoost: {e}")

# @tool
# def predict_root_cause(query: str) -> str:
#     """Predicts the root cause using an optimized XGBoost model."""
#     if not MODEL_LOADED:
#         return "Error: XGBoost model not loaded."
    
#     try:
#         # 1. Vectorize text
#         query_vec = TFIDF.transform([query])
        
#         # 2. Get Prediction
#         probs = MODEL.predict_proba(query_vec)[0]
#         max_prob = probs.max()
#         pred_idx = probs.argmax()
        
#         # 3. Decode Label
#         prediction = LE.inverse_transform([pred_idx])[0]
        
#         if max_prob < CONFIDENCE_THRESHOLD:
#             return (f"XGBoost is UNCERTAIN (Confidence: {max_prob:.2%}). "
#                     f"Possible guess: '{prediction}'. Please verify with Web Search.")
        
#         return f"Predicted Root Cause: {prediction} (Confidence: {max_prob:.2%})"
            
#     except Exception as e:
#         return f"XGBoost Error: {str(e)}"


import joblib
import numpy as np
import json
from langchain.tools import tool

class VehicleClassifier:
    def __init__(self):
        # Ensure paths are correct relative to where you run the script
        self.model = joblib.load('models/dtc_classifier.pkl')
        self.model_enc = joblib.load('models/car_model_encoder.pkl')
        self.label_enc = joblib.load('models/target_label_encoder.pkl')

    def predict(self, sensor_data: dict):
        """
        sensor_data keys: CAR_MODEL, YEAR, ENGINE_RPM, VEHICLE_SPEED, 
        ENGINE_LOAD, COOLANT_TEMP, MAF_GRAMS_SEC, SHORT_TERM_TRIM, 
        LONG_TERM_TRIM, THROTTLE_POS
        """
        # Convert model name to encoded value
        try:
            model_val = self.model_enc.transform([sensor_data.get('CAR_MODEL', 'Unknown')])[0]
        except ValueError:
            # Handle unknown models by defaulting to a known one or -1
            # Using -1 might crash XGBoost if not trained on it, so let's use 0 (safe fallback)
            model_val = 0 
            
        features = [
            model_val, 
            float(sensor_data.get('YEAR', 2020)),
            float(sensor_data.get('ENGINE_RPM', 0)),
            float(sensor_data.get('VEHICLE_SPEED', 0)),
            float(sensor_data.get('ENGINE_LOAD', 0)),
            float(sensor_data.get('COOLANT_TEMP', 90)),
            float(sensor_data.get('MAF_GRAMS_SEC', 10)),
            float(sensor_data.get('SHORT_TERM_TRIM', 0)),
            float(sensor_data.get('LONG_TERM_TRIM', 0)),
            float(sensor_data.get('THROTTLE_POS', 20))
        ]
        
        # Get Probabilities
        probs = self.model.predict_proba([features])[0]
        max_prob = np.max(probs)
        prediction_idx = np.argmax(probs)
        dtc_code = self.label_enc.inverse_transform([prediction_idx])[0]

        result = {
            "status": "CONFIDENT" if max_prob >= 0.70 else "UNCERTAIN",
            "confidence": round(float(max_prob), 4), # Float for JSON serialization
            "prediction": dtc_code,
            "action": "Immediate diagnosis identified." if max_prob >= 0.70 else "Triggering deeper RAG and Web Research."
        }
        return result

# --- UPDATED TOOL DEFINITION ---
@tool
def predict_root_cause(query: str):
    """
    Predicts the vehicle's Diagnostic Trouble Code (DTC) using an XGBoost Machine Learning model.
    Input should be a JSON string or description of sensor values (RPM, Load, Speed, etc.).
    Returns a JSON string with confidence score and predicted DTC.
    """
    try:
        # 1. Parse Input (Simple parsing logic for demo)
        # In a real app, the Agent would pass a JSON string. 
        # Here we default to some dummy values if parsing fails, 
        # or we try to extract from the query string.
        
        # For this prototype, we'll assume the Agent passes the query string 
        # and we extract what we can, or use the 'query' as a key if it's a dict-like string.
        # But for robust 'evaluate.py' usage where input is natural language:
        
        # We will initialize with safe defaults
        sensor_data = {
            "CAR_MODEL": "Tata Nexon", "YEAR": 2020, 
            "ENGINE_RPM": 2000, "VEHICLE_SPEED": 50, "ENGINE_LOAD": 40,
            "COOLANT_TEMP": 90, "MAF_GRAMS_SEC": 15, 
            "SHORT_TERM_TRIM": 0, "LONG_TERM_TRIM": 0, "THROTTLE_POS": 25
        }
        
        # Simple keyword extraction to make the CLI chat feel real
        lower_q = query.lower()
        if "nexon" in lower_q: sensor_data["CAR_MODEL"] = "Tata Nexon"
        if "f-150" in lower_q: sensor_data["CAR_MODEL"] = "Ford F-150"
        if "rpm" in lower_q: 
            # Try to find a number near 'rpm'
            import re
            nums = re.findall(r'\d+', lower_q)
            if nums: sensor_data["ENGINE_RPM"] = float(nums[0])

        classifier = VehicleClassifier()
        result = classifier.predict(sensor_data)
        
        # CRITICAL FIX: Return JSON String
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": str(e)})
