from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    # Input from User
    messages: List[str]  # Chat history
    user_complaint: str
    dtc_codes: List[str]
    sensor_data: dict
    
    # Internal State (Filled by Agents)
    clarification_needed: bool
    diagnostic_context: str  # Data retrieved from RAG
    root_causes: List[dict]  # The result of diagnosis
    repair_plan: dict        # Final output
    
    # Flow Control
    next_step: str
