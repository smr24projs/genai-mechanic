import requests
import json
import uuid

# --- CONFIGURATION ---
import os
from dotenv import load_dotenv

load_dotenv()

# Load from .env, with fallbacks or empty strings if not set
BASE_URL = os.getenv("LANGFLOW_BASE_URL", "http://localhost:7860/api/v1/run/YOUR_FLOW_ID")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "")
# ---------------------

def run_langflow(message: str):
    """
    Sends text to LangFlow and returns the AI's response.
    """
    headers = {"x-api-key": LANGFLOW_API_KEY}
    
    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": message,
        "session_id": str(uuid.uuid4()) # New session for every message
    }

    try:
        response = requests.post(BASE_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Navigate the deep JSON response to find the text
        try:
            # LangFlow v1.0+ structure
            return data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
        except (KeyError, IndexError):
            # Fallback for older versions or different node types
            return f"Raw Response: {data}"

    except Exception as e:
        return f"Error connecting to LangFlow: {str(e)}"