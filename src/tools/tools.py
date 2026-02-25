import pandas as pd
import json
from langchain_core.tools import tool

# Load data once to keep it fast
try:
    DTC_DB = pd.read_csv("data/dtc_codes.csv")
    with open("data/parts_catalog.json", "r") as f:
        PARTS_DB = json.load(f)
except Exception as e:
    # Fallback if files are missing (prevents crash on import)
    print(f"Warning: Data files not loaded in tools.py. {e}")
    DTC_DB = pd.DataFrame()
    PARTS_DB = []

@tool
def lookup_dtc(code: str) -> str:
    """
    Consults the definition of a Diagnostic Trouble Code (DTC).
    Input: A DTC code string (e.g., 'P0300'). 
    Output: Description and symptoms.
    """
    code = code.upper().strip()
    # Simple check if dataframe is empty
    if DTC_DB.empty:
        return "Database not loaded."

    result = DTC_DB[DTC_DB['code'] == code]
    
    if result.empty:
        return f"Code {code} not found in the database."
    
    row = result.iloc[0]
    return f"Code: {row['code']}\nDescription: {row['description']}\nSymptoms: {row['symptoms']}"

@tool
def lookup_parts(repair_context: str) -> str:
    """
    Searches the parts catalog for parts related to a repair.
    Input: A keyword related to the repair (e.g., 'Spark Plug', 'O2 Sensor', 'P0300').
    Output: List of available parts and prices.
    """
    if not PARTS_DB:
        return "Parts catalog not loaded."

    matches = []
    query = repair_context.lower()
    
    for part in PARTS_DB:
        # Check if query matches name or compatibility list
        if query in part['name'].lower() or any(query.upper() in c for c in part['compatibility']):
            matches.append(f"{part['name']} (ID: {part['part_id']}) - ${part['price']}")
            
    if not matches:
        return "No parts found for this repair context."
    
    return "\n".join(matches)
