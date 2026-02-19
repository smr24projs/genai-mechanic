"""
DTC Cascade Classifier Tool
============================
Orchestrates: ML Model (Random Forest) → RAG (AstraDB) → Web Scraper (Tavily)
Returns the best result based on confidence scoring.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

# ──────────────────────────────────────────────
# 1. LOAD ML MODEL ARTIFACTS AT IMPORT TIME
# ──────────────────────────────────────────────
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(MODEL_DIR, "../../"))

try:
    rf_model = joblib.load(os.path.join(PROJECT_ROOT, "rf_dtc_model.pkl"))
    le_car = joblib.load(os.path.join(PROJECT_ROOT, "rf_label_encoder.pkl"))
    class_names = joblib.load(os.path.join(PROJECT_ROOT, "rf_class_names.pkl"))
    ML_READY = True
    print("✅ Random Forest DTC model loaded successfully.")
except Exception as e:
    rf_model = None
    le_car = None
    class_names = None
    ML_READY = False
    print(f"⚠️ Random Forest model not loaded: {e}")

# ──────────────────────────────────────────────
# 2. CONFIDENCE THRESHOLD
# ──────────────────────────────────────────────
ML_CONFIDENCE_THRESHOLD = 60.0  # Percent

# ──────────────────────────────────────────────
# 3. ML PREDICTION FUNCTION
# ──────────────────────────────────────────────
def ml_predict(car_model: str, year: float, engine_rpm: float, vehicle_speed: float,
               engine_load: float, coolant_temp: float, maf_grams_sec: float,
               short_term_trim: float, long_term_trim: float, throttle_pos: float):
    """Run Random Forest prediction and return (prediction, confidence, all_probabilities)."""
    if not ML_READY:
        return None, 0.0, {}

    # Encode car model (handle unseen labels gracefully)
    try:
        car_encoded = le_car.transform([car_model.lower().strip()])[0]
    except ValueError:
        # Unseen car model — use the most common encoded value
        car_encoded = 0

    input_data = pd.DataFrame([{
        'CAR_MODEL_ENCODED': car_encoded,
        'YEAR': year,
        'ENGINE_RPM': engine_rpm,
        'VEHICLE_SPEED': vehicle_speed,
        'ENGINE_LOAD': engine_load,
        'COOLANT_TEMP': coolant_temp,
        'MAF_GRAMS_SEC': maf_grams_sec,
        'SHORT_TERM_TRIM': short_term_trim,
        'LONG_TERM_TRIM': long_term_trim,
        'THROTTLE_POS': throttle_pos
    }])

    prediction = rf_model.predict(input_data)[0]
    probabilities = rf_model.predict_proba(input_data)[0]
    confidence = float(max(probabilities) * 100)

    # Build probability dict for all classes
    prob_dict = {}
    for cls, prob in zip(rf_model.classes_, probabilities):
        prob_dict[cls] = round(float(prob * 100), 2)

    return prediction, confidence, prob_dict


# ──────────────────────────────────────────────
# 4. RAG SEARCH FUNCTION
# ──────────────────────────────────────────────
def rag_search(query: str):
    """Search AstraDB via the existing RAG retriever. Returns (result_text, confidence)."""
    try:
        from src.rag.retriever import query_manuals
        result = query_manuals(query)

        if not result or "No relevant information" in result or "Error" in result:
            return None, 0.0

        # Calculate a simple keyword-match confidence score
        dtc_keywords = ['P0101', 'P0117', 'P0171', 'P0300', 'P2463',
                        'misfire', 'lean', 'coolant', 'temperature', 'sensor',
                        'mass air flow', 'MAF', 'particulate', 'filter',
                        'exhaust', 'oxygen', 'O2', 'fuel trim']

        query_lower = query.lower()
        result_lower = result.lower()

        # Count how many relevant keywords appear in both query and result
        matches = sum(1 for kw in dtc_keywords
                      if kw.lower() in query_lower or kw.lower() in result_lower)
        # Confidence: base 50 + up to 50 from keyword matches
        confidence = min(50.0 + (matches * 5.0), 95.0)

        return result, confidence

    except Exception as e:
        print(f"[CASCADE] RAG search error: {e}")
        return None, 0.0


# ──────────────────────────────────────────────
# 5. WEB SCRAPER FUNCTION
# ──────────────────────────────────────────────
def web_search(query: str):
    """Search the web via Tavily. Returns (result_text, confidence)."""
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return None, 0.0

        from langchain_community.tools.tavily_search import TavilySearchResults
        search_tool = TavilySearchResults(max_results=3)
        results = search_tool.invoke(query)

        if not results:
            return None, 0.0

        # Parse results
        if isinstance(results, list):
            combined = "\n\n".join([
                f"**Source:** {r.get('url', 'N/A')}\n{r.get('content', '')}"
                for r in results if isinstance(r, dict)
            ])
        else:
            combined = str(results)

        if not combined.strip():
            return None, 0.0

        # Calculate similarity confidence based on keyword presence
        dtc_keywords = ['DTC', 'diagnostic', 'trouble code', 'fault', 'sensor',
                        'engine', 'repair', 'fix', 'cause', 'symptom']
        query_words = set(query.lower().split())
        result_lower = combined.lower()

        keyword_matches = sum(1 for kw in dtc_keywords if kw.lower() in result_lower)
        query_word_matches = sum(1 for w in query_words if w in result_lower)

        # Confidence: base 30 + keyword overlap + query word overlap
        confidence = min(30.0 + (keyword_matches * 4.0) + (query_word_matches * 3.0), 85.0)

        return combined, confidence

    except Exception as e:
        print(f"[CASCADE] Web search error: {e}")
        return None, 0.0


# ──────────────────────────────────────────────
# 6. CASCADE ORCHESTRATOR
# ──────────────────────────────────────────────
def cascade_diagnose(car_model: str, year: float, engine_rpm: float,
                     vehicle_speed: float, engine_load: float, coolant_temp: float,
                     maf_grams_sec: float, short_term_trim: float,
                     long_term_trim: float, throttle_pos: float) -> str:
    """
    Cascade DTC Diagnostic Tool.
    
    Pipeline: ML Model → RAG (AstraDB) → Web Scraper (Tavily)
    Returns JSON with prediction, confidence, source, and details.
    """
    result = {
        "source": "NONE",
        "prediction": "UNKNOWN",
        "confidence": 0.0,
        "details": "",
        "cascade_path": [],
        "all_probabilities": {}
    }

    # ── Step 1: ML Model Prediction ──
    ml_prediction, ml_confidence, prob_dict = ml_predict(
        car_model, year, engine_rpm, vehicle_speed,
        engine_load, coolant_temp, maf_grams_sec,
        short_term_trim, long_term_trim, throttle_pos
    )

    result["cascade_path"].append(f"ML_MODEL(confidence={ml_confidence:.1f}%)")
    result["all_probabilities"] = prob_dict

    if ml_prediction and ml_confidence >= ML_CONFIDENCE_THRESHOLD:
        result["source"] = "ML_MODEL (Random Forest)"
        result["prediction"] = ml_prediction
        result["confidence"] = round(ml_confidence, 2)
        result["details"] = (
            f"Random Forest classifier predicted DTC code '{ml_prediction}' "
            f"with {ml_confidence:.1f}% confidence. "
            f"This is above the {ML_CONFIDENCE_THRESHOLD}% threshold."
        )
        return json.dumps(result, indent=2)

    # ── Step 2: RAG Search (AstraDB) ──
    search_query = f"{ml_prediction or ''} {car_model} engine RPM {engine_rpm} coolant {coolant_temp}"
    rag_result, rag_confidence = rag_search(search_query)
    result["cascade_path"].append(f"RAG_ASTRADB(confidence={rag_confidence:.1f}%)")

    if rag_result and rag_confidence > 0:
        # Compare RAG confidence vs ML confidence
        if rag_confidence > ml_confidence:
            result["source"] = "RAG (AstraDB Vector Search)"
            result["prediction"] = ml_prediction if ml_prediction else "See details"
            result["confidence"] = round(rag_confidence, 2)
            result["details"] = rag_result
            return json.dumps(result, indent=2)
        else:
            # ML was still better even though below threshold
            result["source"] = "ML_MODEL (Random Forest) [RAG did not improve confidence]"
            result["prediction"] = ml_prediction
            result["confidence"] = round(ml_confidence, 2)
            result["details"] = (
                f"ML predicted '{ml_prediction}' at {ml_confidence:.1f}%. "
                f"RAG returned results at {rag_confidence:.1f}% confidence but was lower."
            )
            return json.dumps(result, indent=2)

    # ── Step 3: Web Scraper Fallback ──
    web_query = f"{ml_prediction or 'vehicle diagnostic'} {car_model} {year} DTC trouble code"
    web_result, web_confidence = web_search(web_query)
    result["cascade_path"].append(f"WEB_SCRAPER(confidence={web_confidence:.1f}%)")

    if web_result and web_confidence > 0:
        # Compare web confidence vs ML confidence
        if web_confidence > ml_confidence:
            result["source"] = "WEB_SCRAPER (Tavily Search)"
            result["prediction"] = ml_prediction if ml_prediction else "See web results"
            result["confidence"] = round(web_confidence, 2)
            result["details"] = web_result
            return json.dumps(result, indent=2)
        else:
            # ML was still the best
            result["source"] = "ML_MODEL (Random Forest) [Best available confidence]"
            result["prediction"] = ml_prediction
            result["confidence"] = round(ml_confidence, 2)
            result["details"] = (
                f"ML predicted '{ml_prediction}' at {ml_confidence:.1f}%. "
                f"Web search returned {web_confidence:.1f}% confidence but was lower."
            )
            return json.dumps(result, indent=2)

    # ── Fallback: Return ML result even if low confidence ──
    if ml_prediction:
        result["source"] = "ML_MODEL (Random Forest) [Low confidence, no fallback available]"
        result["prediction"] = ml_prediction
        result["confidence"] = round(ml_confidence, 2)
        result["details"] = (
            f"ML predicted '{ml_prediction}' at {ml_confidence:.1f}%. "
            f"RAG and Web Search returned no results."
        )
        return json.dumps(result, indent=2)

    result["details"] = "All diagnostic sources failed. Please check inputs and try again."
    return json.dumps(result, indent=2)


# ──────────────────────────────────────────────
# 7. LANGCHAIN TOOL DEFINITION
# ──────────────────────────────────────────────
class CascadeDiagnosticInput(BaseModel):
    car_model: str = Field(description="Vehicle make and model (e.g., 'nissan versa', 'fiat palio')")
    year: float = Field(description="Vehicle year (e.g., 2016)")
    engine_rpm: float = Field(description="Engine RPM reading")
    vehicle_speed: float = Field(description="Vehicle speed in km/h")
    engine_load: float = Field(description="Engine load percentage")
    coolant_temp: float = Field(description="Engine coolant temperature in °C")
    maf_grams_sec: float = Field(description="Mass Air Flow sensor reading in grams/sec")
    short_term_trim: float = Field(description="Short Term Fuel Trim percentage")
    long_term_trim: float = Field(description="Long Term Fuel Trim percentage")
    throttle_pos: float = Field(description="Throttle Position percentage")


def get_dtc_cascade_tool():
    return StructuredTool.from_function(
        func=cascade_diagnose,
        name="dtc_cascade_diagnostic",
        description=(
            "Advanced DTC diagnostic tool that uses a cascade of sources: "
            "1) ML Random Forest model for DTC prediction with confidence score, "
            "2) RAG search in AstraDB vehicle manuals if ML confidence is low, "
            "3) Web search as final fallback. "
            "Returns JSON with prediction, confidence score (0-100%), source used, "
            "and detailed diagnostic information. "
            "REQUIRES sensor data: car_model, year, engine_rpm, vehicle_speed, "
            "engine_load, coolant_temp, maf_grams_sec, short_term_trim, "
            "long_term_trim, throttle_pos."
        ),
        args_schema=CascadeDiagnosticInput
    )


# ──────────────────────────────────────────────
# 8. TEST FUNCTION
# ──────────────────────────────────────────────
def test_cascade():
    """Quick test of the cascade pipeline."""
    print("=" * 60)
    print("🧪 Testing Cascade Diagnostic Pipeline")
    print("=" * 60)

    # Test case 1: Should trigger P0171 (Lean condition)
    print("\n📋 Test 1: Lean condition (high fuel trims)")
    result = cascade_diagnose(
        car_model="nissan versa", year=2016, engine_rpm=2500,
        vehicle_speed=40, engine_load=85, coolant_temp=95,
        maf_grams_sec=45, short_term_trim=18, long_term_trim=15,
        throttle_pos=55
    )
    parsed = json.loads(result)
    print(f"  Source: {parsed['source']}")
    print(f"  Prediction: {parsed['prediction']}")
    print(f"  Confidence: {parsed['confidence']}%")
    print(f"  Path: {' → '.join(parsed['cascade_path'])}")

    # Test case 2: Should trigger HEALTHY
    print("\n📋 Test 2: Normal operating conditions")
    result = cascade_diagnose(
        car_model="fiat palio", year=2012, engine_rpm=850,
        vehicle_speed=0, engine_load=20, coolant_temp=85,
        maf_grams_sec=10, short_term_trim=1, long_term_trim=2,
        throttle_pos=15
    )
    parsed = json.loads(result)
    print(f"  Source: {parsed['source']}")
    print(f"  Prediction: {parsed['prediction']}")
    print(f"  Confidence: {parsed['confidence']}%")
    print(f"  Path: {' → '.join(parsed['cascade_path'])}")

    # Test case 3: Unknown car model (may trigger lower confidence)
    print("\n📋 Test 3: Unknown car model")
    result = cascade_diagnose(
        car_model="tata nexon", year=2023, engine_rpm=3000,
        vehicle_speed=60, engine_load=70, coolant_temp=105,
        maf_grams_sec=35, short_term_trim=10, long_term_trim=8,
        throttle_pos=45
    )
    parsed = json.loads(result)
    print(f"  Source: {parsed['source']}")
    print(f"  Prediction: {parsed['prediction']}")
    print(f"  Confidence: {parsed['confidence']}%")
    print(f"  Path: {' → '.join(parsed['cascade_path'])}")
    print(f"  All Probabilities: {parsed['all_probabilities']}")

    print("\n" + "=" * 60)
    print("✅ Cascade tests complete!")


if __name__ == "__main__":
    test_cascade()
