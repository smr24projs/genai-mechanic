import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load .env explicitly
load_dotenv()

key = os.getenv("GOOGLE_API_KEY")
print(f"API Key loaded: {'Yes' if key else 'NO'}")
if key:
    print(f"Key starts with: {key[:5]}...")

# 2. Try a simple invocation
try:
    print("\nAttempting to connect to Gemini...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", # Try "gemini-pro" if this fails
        google_api_key=key,
        temperature=0
    )
    result = llm.invoke("Hello, are you working?")
    print(f"\nSUCCESS! Response: {result.content}")
except Exception as e:
    print(f"\nFAILURE. Error details:\n{e}")
