import sys
from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents.nodes import advisor_node, diagnostic_node, repair_node

# --- 1. Define the Graph Logic ---
def build_app():
    # Initialize the graph with our State class
    workflow = StateGraph(AgentState)

    # Add the nodes (The Agents)
    workflow.add_node("advisor", advisor_node)
    workflow.add_node("diagnostic", diagnostic_node)
    workflow.add_node("repair", repair_node)

    # Set the entry point
    workflow.set_entry_point("advisor")

    # --- 2. Define the Edges (The Flow) ---
    
    # Conditional Edge: Advisor -> User OR Advisor -> Diagnosis
    def advisor_logic(state):
        if state['next_step'] == "ask_user":
            return END  # Stop and return control to the user (UI)
        return "diagnostic"
    
    workflow.add_conditional_edges(
        "advisor",
        advisor_logic,
        {
            END: END,
            "diagnostic": "diagnostic"
        }
    )

    # Linear Edges: Diagnosis -> Repair -> End
    workflow.add_edge("diagnostic", "repair")
    workflow.add_edge("repair", END)

    # Compile the graph
    app = workflow.compile()
    return app

# --- 3. CLI Loop (For Testing in Terminal) ---
if __name__ == "__main__":
    print("🚗 GenAI Mechanic is Online! (Type 'quit' to exit)")
    
    app = build_app()
    
    # Initialize basic state
    # In a real app, the UI would capture these values.
    # We will simulate a user describing a problem.
    initial_state = {
        "messages": [],
        "user_complaint": "",
        "dtc_codes": [],
        "sensor_data": {},
        "root_causes": [],
        "repair_plan": {},
        "next_step": ""
    }
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        # Append user message to state
        initial_state["messages"].append(user_input)
        
        # NOTE: Manual injection for CLI testing
        if "P0300" in user_input:
            initial_state["dtc_codes"] = ["P0300"]
            initial_state["user_complaint"] = user_input
            initial_state["sensor_data"] = {"fuel_trim": "High (+15%)"}
        
        elif "P0171" in user_input:
            initial_state["dtc_codes"] = ["P0171"]
            initial_state["user_complaint"] = user_input
            # P0171 usually means Lean, so we simulate appropriate sensor data
            initial_state["sensor_data"] = {"fuel_trim": "Positive (+25%)", "o2_voltage": "Low (0.1V)"}
        
        # Run the Graph
        print("🤖 Processing...")
        for event in app.stream(initial_state):
            for key, value in event.items():
                # Print agent activity
                if "messages" in value:
                    print(f"\n[Agent]: {value['messages'][-1]}")
                
                # Update our local state for the next loop
                initial_state.update(value)