# import os
# from dotenv import load_dotenv
# from typing import List
# from pydantic import BaseModel, Field, validator
# from langchain_core.output_parsers import PydanticOutputParser
# from langchain_core.prompts import PromptTemplate
# from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
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
from dotenv import load_dotenv
from typing import List, Dict, Any, Annotated
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, ToolMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
import operator

# Import custom tools
from src.tools.classifier_tool import predict_root_cause
from src.tools.rag_tool import vehicle_diagnostic_db
from src.tools.web_search import vehicle_web_search

load_dotenv()

# ==========================================
# 1. TERMINAL FORMATTING HELPER
# ==========================================
class TerminalLogger:
    @staticmethod
    def header(title: str):
        print(f"\n{'='*20} {title.upper()} {'='*20}")

    @staticmethod
    def info(label: str, content: Any):
        print(f"🔹 [{label}]: {content}")

    @staticmethod
    def tool_result(tool_name: str, result: str):
        print(f"\n📦 [TOOL OUTPUT: {tool_name}]")
        print(f"{'-'*50}")
        # Show first 800 chars in a clean block
        print(result[:800] + "..." if len(result) > 800 else result)
        print(f"{'-'*50}\n")

# ==========================================
# 2. OUTPUT SCHEMA & STATE
# ==========================================
class DiagnosticResponse(BaseModel):
    needs_more_info: bool
    clarifying_questions: List[str]
    diagnosis: str
    confidence_level: str
    ml_evidence: str
    rag_evidence: str
    web_evidence: str
    action_plan: List[str]
    safety_warning: str

parser = PydanticOutputParser(pydantic_object=DiagnosticResponse)

class AgentState(BaseModel):
    messages: Annotated[List[BaseMessage], operator.add]

# ==========================================
# 3. NODES WITH ENHANCED LOGGING
# ==========================================
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
tools = [predict_root_cause, vehicle_diagnostic_db, vehicle_web_search]
llm_with_tools = llm.bind_tools(tools)

def diagnostic_reasoner(state: AgentState):
    TerminalLogger.header("Agent Reasoning")
    
    agent_template = f"""You are a Master Diagnostic AI. Format response ONLY as JSON:
    {parser.get_format_instructions()}"""
    
    messages = [SystemMessage(content=agent_template)] + state.messages
    response = llm_with_tools.invoke(messages)
    
    if response.tool_calls:
        for t in response.tool_calls:
            TerminalLogger.info("Action", f"Calling tool '{t['name']}' with args {t['args']}")
    return {"messages": [response]}

def tool_logger_node(state: AgentState):
    last_msg = state.messages[-1]
    if isinstance(last_msg, ToolMessage):
        # Find which tool was just run
        tool_name = "Unknown Tool"
        for msg in reversed(state.messages[:-1]):
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_name = msg.tool_calls[0]['name']
                break
        TerminalLogger.tool_result(tool_name, last_msg.content)
    return state

# ==========================================
# 4. GRAPH CONSTRUCTION
# ==========================================
workflow = StateGraph(AgentState)
workflow.add_node("reasoner", diagnostic_reasoner)
workflow.add_node("tools", ToolNode(tools))
workflow.add_node("logger", tool_logger_node)

workflow.add_edge(START, "reasoner")
workflow.add_conditional_edges("reasoner", lambda x: "tools" if x.messages[-1].tool_calls else END)
workflow.add_edge("tools", "logger")
workflow.add_edge("logger", "reasoner")

langgraph_app = workflow.compile()

# ==========================================
# 5. WRAPPER (FINAL LOGGING)
# ==========================================
class LegacyAgentExecutorWrapper:
    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        TerminalLogger.header("New Session Initiated")
        TerminalLogger.info("Input", inputs.get("input")[:100] + "...")
        
        result = langgraph_app.invoke({"messages": [HumanMessage(content=inputs.get("input", ""))]})
        
        final_content = result["messages"][-1].content
        TerminalLogger.header("Final Agent Verdict")
        try:
            # Try to print pretty-printed JSON
            parsed = json.loads(final_content.replace("```json", "").replace("```", "").strip())
            print(json.dumps(parsed, indent=4))
        except:
            print(final_content)
        print("="*50 + "\n")
        
        return {"output": final_content}
    
    def get_graph(self):
        return langgraph_app.get_graph()

agent_executor = LegacyAgentExecutorWrapper()