import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env")
else:
    genai.configure(api_key=api_key)
    print("--- 🔍 AVAILABLE EMBEDDING MODELS ---")
    try:
        found = False
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                print(f"✅ Found: {m.name}")
                found = True
        if not found:
            print("❌ No embedding models found. Check your API Key permissions.")
    except Exception as e:
        print(f"Error listing models: {e}")
