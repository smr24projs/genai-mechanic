import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Any, Annotated
from typing_extensions import TypedDict
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
        print(str(result)[:800] + "..." if len(str(result)) > 800 else str(result))
        print(f"{'-'*50}\n")

# ==========================================
# 2. OUTPUT SCHEMA & STATE
# ==========================================
class DiagnosticResponse(BaseModel):
    needs_more_info: bool = Field(description="Set to True if the prompt is too vague.")
    clarifying_questions: List[str] = Field(description="Questions to ask if needs_more_info is True.")
    diagnosis: str = Field(description="Main diagnostic text. Use Markdown bullet points for lists of tools, parts, or specifications.")
    confidence_level: str = Field(description="High, Medium, or Low")
    confidence_score: int = Field(description="Overall confidence percentage (0-100)")
    rag_score: int = Field(description="Integer 0-100 reflecting RAG knowledge match.")
    ml_score: int = Field(description="Integer 0-100 reflecting the ML classifier confidence. Extract exactly from tool output.")
    web_score: int = Field(description="Integer 0-100 reflecting web search relevance.")
    ml_evidence: str = Field(description="Evidence from ML")
    rag_evidence: str = Field(description="Evidence from RAG")
    web_evidence: str = Field(description="Evidence from Web")
    action_plan: List[str] = Field(description="ONLY for sequential, step-by-step physical repair procedures. MUST BE EMPTY [] if answering tool requests, specs, or general info.")
    safety_warning: str = Field(description="Critical safety warnings, or 'None'")

parser = PydanticOutputParser(pydantic_object=DiagnosticResponse)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    decision_log: Annotated[List[str], operator.add]

# ==========================================
# 3. NODES
# ==========================================
llm = ChatGoogleGenerativeAI(
    model=os.getenv("MODEL_NAME", "gemini-2.5-flash"),
    temperature=0.2,
    google_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
)
tools = [predict_root_cause, vehicle_diagnostic_db, vehicle_web_search]
llm_with_tools = llm.bind_tools(tools)

def diagnostic_reasoner(state: AgentState):
    TerminalLogger.header("Agent Reasoning")
    
    agent_template = f"""You are a Master Diagnostic AI for vehicle troubleshooting.

STEP 1 - TOOLS: You MUST call predict_root_cause, vehicle_diagnostic_db, and vehicle_web_search to gather evidence.

CRITICAL — predict_root_cause query format:
You MUST pass a JSON string with the EXACT numeric sensor values from the input. Do NOT paraphrase.
Example: {{"CAR_MODEL": "Tata", "ENGINE_RPM": 1900, "VEHICLE_SPEED": 0, "ENGINE_LOAD": 92, "COOLANT_TEMP": 90, "MAF_GRAMS_SEC": 0, "SHORT_TERM_TRIM": 0, "LONG_TERM_TRIM": 0, "THROTTLE_POS": 20, "DTC": "P2463"}}

STEP 2 - SCORES: After running the tools, you MUST read the score hints they return:
- From predict_root_cause output → read 'ml_score_hint' (integer 0-100). Use this EXACTLY as ml_score. Do not guess it.
- From vehicle_diagnostic_db output → read 'RAG_SCORE_HINT' (integer 0-100). Use this EXACTLY as rag_score.
- Web Search Score (web_score): Evaluate the string returned by vehicle_web_search (0-100).
- confidence_score = MAXIMUM of (ml_score, rag_score, web_score).

STEP 3 - FORMATTING RULES:
- If the user asks for a repair procedure, put the sequential steps in the 'action_plan' array.
- If the user asks for a LIST OF TOOLS, PARTS, or TORQUE SPECS, put the list inside the 'diagnosis' string using Markdown bullet points. Leave 'action_plan' COMPLETELY EMPTY [].
- Output ONLY this JSON object (no other text):
{parser.get_format_instructions()}"""
    
    messages = [SystemMessage(content=agent_template)] + state['messages']
    response = llm_with_tools.invoke(messages)
    
    decision_entry = []
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for t in response.tool_calls:
            TerminalLogger.info("Action", f"Calling tool '{t['name']}' with args {t['args']}")
            decision_entry.append(f"REASONER → Calling {t['name']}")
    else:
        decision_entry.append("REASONER → Synthesizing final answer")
        
    return {"messages": [response], "decision_log": decision_entry}

def tool_logger_node(state: AgentState):
    decision_entry = []
    last_msg = state['messages'][-1]
    if isinstance(last_msg, ToolMessage):
        tool_name = last_msg.name if hasattr(last_msg, 'name') and last_msg.name else "Tool"
        TerminalLogger.tool_result(tool_name, last_msg.content)
        
        if 'predict_root_cause' in tool_name:
            decision_entry.append(f"ML CLASSIFIER → Tool Output Received")
        elif 'vehicle_diagnostic_db' in tool_name:
            decision_entry.append(f"RAG DATABASE → Tool Output Received")
        elif 'vehicle_web_search' in tool_name:
            decision_entry.append(f"WEB SEARCH → Tool Output Received")
            
    return {"decision_log": decision_entry}

# ==========================================
# 4. GRAPH CONSTRUCTION
# ==========================================
def _route_reasoner(state: AgentState) -> str:
    last_msg = state['messages'][-1]
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        return "tools"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("reasoner", diagnostic_reasoner)
workflow.add_node("tools", ToolNode(tools))
workflow.add_node("logger", tool_logger_node)

workflow.add_edge(START, "reasoner")
workflow.add_conditional_edges("reasoner", _route_reasoner)
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
        
        result = langgraph_app.invoke({"messages": [HumanMessage(content=inputs.get("input", ""))], "decision_log": []})
        
        final_content = result["messages"][-1].content
        decision_log = result.get("decision_log", [])
        TerminalLogger.header("Final Agent Verdict")
        try:
            parsed = json.loads(final_content.replace("```json", "").replace("```", "").strip())
            print(json.dumps(parsed, indent=4))
        except:
            print(final_content)
        print("="*50 + "\n")
        
        return {"output": final_content, "decision_log": decision_log}
    
    def get_graph(self):
        return langgraph_app.get_graph()

agent_executor = LegacyAgentExecutorWrapper()