from dotenv import load_dotenv
import os
import pandas as pd
from src.state import AgentState

load_dotenv()

def test_environment():
    # 1. Check API Key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in .env")
    else:
        print("✅ API Key detected.")

    # 2. Check Data
    try:
        df = pd.read_csv("data/dtc_codes.csv")
        print(f"✅ Data loaded. Found {len(df)} DTC codes.")
    except FileNotFoundError:
        print("❌ Error: dtc_codes.csv not found. Run setup_data.py first.")

    # 3. Check State Import
    state = AgentState(user_complaint="Test", dtc_codes=[], messages=[], sensor_data={}, clarification_needed=False, diagnostic_context="", root_causes=[], repair_plan={}, next_step="")
    print("✅ AgentState class is working.")

if __name__ == "__main__":
    test_environment()
