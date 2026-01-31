import requests
import json
import uuid

# --- CONFIGURATION ---
# I took this URL directly from your screenshot:
BASE_URL = "http://localhost:7860/api/v1/run/474947e5-2296-4de5-98d0-91a2d23b3c54"

# PASTE YOUR KEY HERE (keep the quotes!)
LANGFLOW_API_KEY = "sk-shFOBwZ8kJxwMw5wlxZzT8ekBdKsRuXhRZcPJZQXhAc" 
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