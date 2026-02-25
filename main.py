# import sys
# from langgraph.graph import StateGraph, END
# from src.state import AgentState
# from src.agents.nodes import advisor_node, diagnostic_node, repair_node

# # --- 1. Define the Graph Logic ---
# def build_app():
#     # Initialize the graph with our State class
#     workflow = StateGraph(AgentState)

#     # Add the nodes (The Agents)
#     workflow.add_node("advisor", advisor_node)
#     workflow.add_node("diagnostic", diagnostic_node)
#     workflow.add_node("repair", repair_node)

#     # Set the entry point
#     workflow.set_entry_point("advisor")

#     # --- 2. Define the Edges (The Flow) ---
    
#     # Conditional Edge: Advisor -> User OR Advisor -> Diagnosis
#     def advisor_logic(state):
#         if state['next_step'] == "ask_user":
#             return END  # Stop and return control to the user (UI)
#         return "diagnostic"
    
#     workflow.add_conditional_edges(
#         "advisor",
#         advisor_logic,
#         {
#             END: END,
#             "diagnostic": "diagnostic"
#         }
#     )

#     # Linear Edges: Diagnosis -> Repair -> End
#     workflow.add_edge("diagnostic", "repair")
#     workflow.add_edge("repair", END)

#     # Compile the graph
#     app = workflow.compile()
#     return app

# # --- 3. CLI Loop (For Testing in Terminal) ---
# if __name__ == "__main__":
#     print("🚗 GenAI Mechanic is Online! (Type 'quit' to exit)")
    
#     app = build_app()
    
#     # Initialize basic state
#     # In a real app, the UI would capture these values.
#     # We will simulate a user describing a problem.
#     initial_state = {
#         "messages": [],
#         "user_complaint": "",
#         "dtc_codes": [],
#         "sensor_data": {},
#         "root_causes": [],
#         "repair_plan": {},
#         "next_step": ""
#     }
    
#     while True:
#         user_input = input("\nUser: ")
#         if user_input.lower() in ["quit", "exit"]:
#             break
            
#         # Append user message to state
#         initial_state["messages"].append(user_input)
        
#         # NOTE: Manual injection for CLI testing
#         if "P0300" in user_input:
#             initial_state["dtc_codes"] = ["P0300"]
#             initial_state["user_complaint"] = user_input
#             initial_state["sensor_data"] = {"fuel_trim": "High (+15%)"}
        
#         elif "P0171" in user_input:
#             initial_state["dtc_codes"] = ["P0171"]
#             initial_state["user_complaint"] = user_input
#             # P0171 usually means Lean, so we simulate appropriate sensor data
#             initial_state["sensor_data"] = {"fuel_trim": "Positive (+25%)", "o2_voltage": "Low (0.1V)"}
        
#         # Run the Graph
#         print("🤖 Processing...")
#         for event in app.stream(initial_state):
#             for key, value in event.items():
#                 # Print agent activity
#                 if "messages" in value:
#                     print(f"\n[Agent]: {value['messages'][-1]}")
                
#                 # Update our local state for the next loop
#                 initial_state.update(value)


import sys
import os
import warnings

# --- 1. SETUP PATHS & WARNINGS ---
# Add the current directory to Python's path so it can find 'src'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Suppress the Google Generative AI deprecation warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from dotenv import load_dotenv
from langchain_core.globals import set_debug

# --- 2. LOAD ENVIRONMENT VARIABLES ---
# Force load .env from the current directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# --- 3. IMPORT AGENT ---
try:
    from src.agents.advisor import build_advisor_agent
except ImportError as e:
    print("\nCRITICAL ERROR: Could not import the agent.")
    print(f"Details: {e}")
    print("Ensure you have __init__.py files in your 'src' and 'src/agents' folders.\n")
    sys.exit(1)

# --- 4. DEBUG MODE (Optional) ---
# Set to True if you want to see exactly what the agent is thinking/doing
DEBUG_MODE = True
if DEBUG_MODE:
    set_debug(True)

def main():
    # Check for API Key
    if not os.getenv("GOOGLE_API_KEY"):
        print("\nERROR: GOOGLE_API_KEY not found in .env file.")
        print("Please create a .env file with: GOOGLE_API_KEY=your_key_here")
        return

    print("Initializing Vehicle Diagnostic Agent...")
    try:
        agent_executor = build_advisor_agent()
    except Exception as e:
        print(f"\nFailed to build agent: {e}")
        return

    print("\n" + "="*40)
    print(" 🚗  VEHICLE DIAGNOSTIC SYSTEM READY")
    print("="*40)
    print("Type 'exit' or 'quit' to stop.")
    print("Examples:")
    print(" - 'What is code P0300?' (Uses RAG)")
    print(" - 'Recalls for 2024 Toyota Tacoma?' (Uses Web Search)")
    print("="*40 + "\n")

    while True:
        try:
            user_input = input("User: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Shutting down...")
                break
            
            if not user_input:
                continue

            print("\nAdvisor is thinking...")
            
            # Run the agent
            response = agent_executor.invoke({"input": user_input})
            
            # Output the result
            output_text = response.get('output', "No response generated.")
            print(f"Advisor: {output_text}\n")

        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}\n")

if __name__ == "__main__":
    main()
