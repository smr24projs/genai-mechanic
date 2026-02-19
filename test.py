import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Load the Environment Variables from the .env file
load_dotenv()

# 2. Get the key by its NAME, not the value
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env file.")
else:
    print(f"✅ Found API Key: {api_key[:5]}... (hidden)")
    
    # 3. Test the connection
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Are you working?")
        print(f"✅ Success! Gemini replied: {response.text}")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")