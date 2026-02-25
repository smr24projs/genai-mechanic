import requests
import json
import uuid

# --- CONFIGURATION ---
# I took this URL directly from your screenshot:
# BASE_URL = "http://localhost:7860/api/v1/run/474947e5-2296-4de5-98d0-91a2d23b3c54"
# BASE_URL = "http://localhost:7860/api/v1/run/e88d1a80-6911-459e-ac54-5328a9f81a77"
BASE_URL = "http://localhost:7860/api/v1/run/59245bc1-3275-454d-81cb-63ca17f2ee34"
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

# import requests
# from typing import Optional

# # --- CONFIGURATION ---

# # 1. Your Flow ID (I have pre-filled this for you)
# FLOW_ID = "59245bc1-3275-454d-81cb-63ca17f2ee34"

# # 2. PASTE YOUR NEW API KEY HERE
# # It should look like: "sk-..."
# APPLICATION_TOKEN = "sk-shFOBwZ8kJxwMw5wlxZzT8ekBdKsRuXhRZcPJZQXhAc"

# # 3. Base API URL
# BASE_API_URL = "http://localhost:7860"

# def run_flow(message: str,
#   endpoint: str = FLOW_ID,
#   output_type: str = "chat",
#   input_type: str = "chat",
#   tweaks: Optional[dict] = None,
#   application_token: Optional[str] = None) -> dict:
#     """
#     Runs a LangFlow flow by sending a POST request to the API.
#     """
#     api_url = f"{BASE_API_URL}/api/v1/run/{endpoint}"

#     payload = {
#         "input_value": message,
#         "output_type": output_type,
#         "input_type": input_type,
#     }
    
#     headers = {
#         "Content-Type": "application/json"
#     }
    
#     # Logic to handle the API Key Authentication
#     if application_token:
#         headers["Authorization"] = f"Bearer {application_token}"
#     elif APPLICATION_TOKEN and APPLICATION_TOKEN != "PASTE_YOUR_GENERATED_KEY_HERE":
#         headers["Authorization"] = f"Bearer {APPLICATION_TOKEN}"

#     try:
#         response = requests.post(api_url, json=payload, headers=headers)
        
#         # If the token is wrong, this will print the exact error
#         if response.status_code == 403:
#             raise Exception("Authentication Error: Your API Key is invalid or missing.")
            
#         response.raise_for_status()
#         return response.json()
        
#     except requests.exceptions.RequestException as e:
#         print(f"❌ API Error: {e}")
#         return {"error": str(e)}
