import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.prompts import ADVISOR_PROMPT, DIAGNOSTIC_PROMPT, REPAIR_PROMPT
from src.state import AgentState
from src.tools.tools import lookup_parts, lookup_dtc
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

# Setup the LLM
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY not found in .env")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", # Fast and efficient
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)

# --- Node 1: Service Advisor ---
def advisor_node(state: AgentState):
    """Checks if we have enough info to proceed."""
    user_input = state['messages'][-1] if state['messages'] else ""
    
    # format the prompt
    chain = ADVISOR_PROMPT | llm
    response = chain.invoke({"input": user_input})
    
    if "READY" in response.content:
        # If ready, we don't reply to user yet, we pass to diagnosis
        return {"next_step": "diagnose"}
    else:
        # If not ready, we ask the user the question
        return {
            "messages": [response.content],
            "next_step": "ask_user"
        }

# --- Node 2: Diagnostic Specialist ---
def diagnostic_node(state: AgentState):
    """Performs RAG and analysis."""
    print("🔧 Diagnosing...")
    
    # 1. Retrieve Context (Simple RAG simulation for now)
    # In a full app, we would query the ChromaDB here. 
    # For this step, we'll fetch the definition of the DTC codes as context.
    dtc_context = ""
    for code in state.get('dtc_codes', []):
        dtc_context += lookup_dtc.invoke(code) + "\n"
        
    # 2. Run LLM
    chain = DIAGNOSTIC_PROMPT | llm
    response = chain.invoke({
        "context": dtc_context,
        "complaint": state.get('user_complaint', 'N/A'),
        "dtc": state.get('dtc_codes', []),
        "sensors": state.get('sensor_data', {})
    })
    
    # 3. Parse JSON output
    try:
        # Clean up markdown code blocks if Gemini adds them
        content = response.content.replace("```json", "").replace("```", "").strip()
        analysis = json.loads(content)
        return {
            "root_causes": [analysis],
            "next_step": "plan_repair"
        }
    except Exception as e:
        print(f"Error parsing diagnosis: {e}")
        return {"next_step": "failed"}

# --- Node 3: Repair Technician ---
def repair_node(state: AgentState):
    """Generates the repair plan."""
    print("🛠️ Planning Repair...")
    
    root_cause_data = state['root_causes'][0]
    cause_name = root_cause_data['root_cause']
    
    # 1. Lookup Parts (Tool Call)
    parts_info = lookup_parts.invoke(cause_name)
    
    # 2. Generate Plan
    chain = REPAIR_PROMPT | llm
    response = chain.invoke({
        "root_cause": cause_name
    })
    
    plan = response.content
    
    # Append parts info
    final_output = f"{plan}\n\n**Parts Catalog Match:**\n{parts_info}"
    
    return {
        "repair_plan": {"text": final_output},
        "messages": [final_output], # This sends the final result to the user
        "next_step": "finished"
    }
