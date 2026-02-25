# import os
# from dotenv import load_dotenv
# from typing import List
# from pydantic import BaseModel, Field, validator
# from langchain.output_parsers import PydanticOutputParser
# from langchain.prompts import PromptTemplate
# from langchain.agents import create_tool_calling_agent, AgentExecutor
# from langchain_google_genai import ChatGoogleGenerativeAI

# # Import your custom tools
# from src.tools.classifier_tool import predict_root_cause
# from src.tools.rag_tool import vehicle_diagnostic_db
# from src.tools.web_search import vehicle_web_search

# load_dotenv()

# # ==========================================
# # 1. DEFINE THE STRICT VALIDATION SCHEMA
# # ==========================================
# class DiagnosticResponse(BaseModel):
#     # --- CLARIFICATION FIELDS ---
#     needs_more_info: bool = Field(description="Set to True ONLY IF the user prompt is too vague (no DTCs, no sensor data, generic complaint). False otherwise.")
#     clarifying_questions: List[str] = Field(description="If needs_more_info is True, list 1-3 specific questions to ask the mechanic. Else empty list.")
    
#     # --- EXISTING DIAGNOSTIC FIELDS ---
#     diagnosis: str = Field(description="The final diagnosis. Write 'Pending' if needs_more_info is True.")
#     confidence_level: str = Field(description="High, Medium, or Low. Write 'None' if needs_more_info is True.")
#     ml_evidence: str = Field(description="Summary of ML findings. Write 'None' if not used.")
#     rag_evidence: str = Field(description="Summary of RAG findings. Write 'None' if not used.")
#     web_evidence: str = Field(description="Summary of Web findings. Write 'None' if not used.")
#     action_plan: List[str] = Field(description="Step-by-step repair instructions. If needs_more_info is True, return ['Pending'].")
#     safety_warning: str = Field(description="Any critical safety warnings. If none, write 'None'.")

#     # Logical Cross-Check Validation
#     @validator('action_plan')
#     def validate_action_plan_sources(cls, action_plan, values):
#         """Ensures the LLM doesn't hallucinate an action plan without evidence."""
        
#         # BYPASS: If the AI just needs more info, skip the strict evidence validation
#         if values.get('needs_more_info') is True:
#             return action_plan
            
#         ml = values.get('ml_evidence', 'None')
#         rag = values.get('rag_evidence', 'None')
#         web = values.get('web_evidence', 'None')
        
#         if ml == 'None' and rag == 'None' and web == 'None':
#             raise ValueError("Validation Failed: Action plan generated without citing any tool evidence.")
        
#         if len(action_plan) == 0:
#             raise ValueError("Validation Failed: Action plan cannot be empty.")
            
#         return action_plan

# # Initialize the Parser
# parser = PydanticOutputParser(pydantic_object=DiagnosticResponse)

# # ==========================================
# # 2. INITIALIZE THE LLM & TOOLS
# # ==========================================
# # Using the stable Gemini 2.5 Flash model as requested
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

# # List of tools the agent can use
# tools = [predict_root_cause, vehicle_diagnostic_db, vehicle_web_search]

# # ==========================================
# # 3. BUILD THE PROMPT TEMPLATE
# # ==========================================
# agent_template = """
# You are a Master Diagnostic Technician AI designed for COMPLEX vehicle troubleshooting.
# You are assisting a professional mechanic. Do not give basic, consumer-level advice (like "check the gas cap").

# Use your ML, RAG, and Web Search tools to find deep, technical root causes such as:
# - Wiring harness chafing or pin-fitment issues.
# - Corrupted module communications (U-codes).
# - Subtle sensor biases (e.g., O2 sensors stuck lean, MAP sensor skewed).
# - Complex mechanical failures (e.g., VVT phaser failure, DPF blockage, internal transmission leaks).

# Analyze the mechanic's provided UI Selections, DTCs, and live data to formulate a comprehensive verdict.

# CRITICAL INSTRUCTION: You MUST format your FINAL output exactly according to these rules:
# {format_instructions}
# Do not include any conversational text outside of the JSON block in your final answer.

# User Query: {input}
# {agent_scratchpad}
# """

# prompt = PromptTemplate(
#     template=agent_template,
#     input_variables=["input", "agent_scratchpad"],
#     partial_variables={"format_instructions": parser.get_format_instructions()}
# )

# # ==========================================
# # 4. CREATE THE AGENT EXECUTOR
# # ==========================================
# agent = create_tool_calling_agent(llm, tools, prompt)

# # The AgentExecutor handles the actual running and tool invoking
# agent_executor = AgentExecutor(
#     agent=agent, 
#     tools=tools, 
#     verbose=True, 
#     handle_parsing_errors=True,
#     max_iterations=5 # Prevents infinite loops
# )


import os
import json
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
# from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import PydanticOutputParser
# from langchain.prompts import PromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. DEFINE THE GRAPH STATE
# ==========================================
class AgentState(TypedDict):
    mechanic_input: str
    is_valid: bool
    clarifying_questions: str
    ui_main_heading: str
    ui_steps_heading: str
    rag_context: str
    web_context: str
    final_raw_output: str

llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

# ==========================================
# 2. DEFINE SCHEMAS & PARSERS
# ==========================================
class GatekeeperResponse(BaseModel):
    is_valid: bool = Field(description="True if prompt has technical detail OR is a direct request for a specific repair procedure. False if too generic.")
    clarifying_questions: str = Field(description="If False, provide 2-3 specific technical questions. If True, write 'None'.")
    ui_main_heading: str = Field(description="A 2-4 word contextual title for the main AI response.")
    ui_steps_heading: str = Field(description="A 2-4 word contextual title for the bulleted list.")

class DiagnosticResponse(BaseModel):
    diagnosis: str = Field(description="Detailed explanation of the issue or repair procedure.")
    confidence_level: str = Field(description="High, Medium, or Low.")
    safety_warning: str = Field(description="Safety warnings, or 'None'.")
    ml_evidence: str = Field(description="Mock ML evidence.")
    rag_evidence: str = Field(description="Mock RAG manuals evidence.")
    web_evidence: str = Field(description="Mock Web TSB evidence.")
    action_plan: list[str] = Field(description="Step by step list of actions.")

gatekeeper_parser = PydanticOutputParser(pydantic_object=GatekeeperResponse)
diagnostic_parser = PydanticOutputParser(pydantic_object=DiagnosticResponse)

# ==========================================
# 3. DEFINE AGENT NODES
# ==========================================
def gatekeeper_node(state: AgentState):
    prompt = PromptTemplate(
        template="Evaluate Mechanic Input.\n{input}\n{format_instructions}",
        input_variables=["input"],
        partial_variables={"format_instructions": gatekeeper_parser.get_format_instructions()}
    )
    chain = prompt | llm_flash | gatekeeper_parser
    result = chain.invoke({"input": state["mechanic_input"]})
    
    return {
        "is_valid": result.is_valid,
        "clarifying_questions": result.clarifying_questions,
        "ui_main_heading": result.ui_main_heading,
        "ui_steps_heading": result.ui_steps_heading
    }

def rag_agent_node(state: AgentState):
    # Mocking RAG retrieval for this example
    return {"rag_context": "Found relevant torque specs and service manuals in AstraDB."}

def web_agent_node(state: AgentState):
    # Mocking Web retrieval for this example
    return {"web_context": "Found 2 related Technical Service Bulletins on NHTSA."}

def diagnostic_judge_node(state: AgentState):
    prompt = PromptTemplate(
        template="""
        You are the Master Diagnostic Judge. Using the input and context, provide a final diagnosis and action plan.
        Input: {input}
        RAG: {rag}
        Web: {web}
        {format_instructions}
        """,
        input_variables=["input", "rag", "web"],
        partial_variables={"format_instructions": diagnostic_parser.get_format_instructions()}
    )
    chain = prompt | llm_flash
    raw_response = chain.invoke({
        "input": state["mechanic_input"],
        "rag": state.get("rag_context", ""),
        "web": state.get("web_context", "")
    })
    return {"final_raw_output": raw_response.content}

# ==========================================
# 4. BUILD THE LANGGRAPH WORKFLOW
# ==========================================
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("Gatekeeper", gatekeeper_node)
workflow.add_node("RAG_Database", rag_agent_node)
workflow.add_node("Web_Search", web_agent_node)
workflow.add_node("Diagnostic_Judge", diagnostic_judge_node)

# Set Entry Point
workflow.add_edge(START, "Gatekeeper")

# Define Routing Logic
def route_triage(state: AgentState):
    if state.get("is_valid") == True:
        return "RAG_Database" # Move to next agent if valid
    return END # Halt flow if invalid

# Add Edges
workflow.add_conditional_edges("Gatekeeper", route_triage)
workflow.add_edge("RAG_Database", "Web_Search")
workflow.add_edge("Web_Search", "Diagnostic_Judge")
workflow.add_edge("Diagnostic_Judge", END)

# Compile!
workflow_app = workflow.compile()