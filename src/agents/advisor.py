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

load_dotenv(override=True)

# ==========================================
# 1. BPMN NOTATION LOGGER (INDUSTRY-STANDARD)
# ==========================================
"""
BPMN Symbol Legend:
  ● = Process Start/End (Terminator)
  ▶ = Task/Process Execution
  ◇ = Exclusive Gateway (Decision Point)
  ⬢ = Service Task / Tool Invocation
  ▬▶ = Sequence Flow / Control Flow
  [M] = Message/Data Flow
"""
class BPMNLogger:
    @staticmethod
    def header(title: str):
        """BPMN: Mark major process phase"""
        print(f"\n{'='*70}")
        print(f"  ● [{title.upper()}]")
        print(f"{'='*70}")

    @staticmethod
    def task_start(task_name: str, details: Any = None):
        """BPMN: Process task initiated"""
        detail_str = f" | {details}" if details else ""
        print(f"  ▶ TASK: {task_name}{detail_str}")

    @staticmethod
    def decision_point(condition: str, decision: str):
        """BPMN: Decision gateway"""
        print(f"  ◇ DECISION: {condition} → {decision}")

    @staticmethod
    def service_invocation(tool_name: str, args: Dict[str, Any] = None):
        """BPMN: Service task (tool) invoked"""
        args_str = f" | Args: {str(args)[:80]}..." if args else ""
        print(f"  ⬢ SERVICE: {tool_name}{args_str}")

    @staticmethod
    def data_flow(source: str, target: str, data: str = None):
        """BPMN: Data/message flow between components"""
        data_str = f" [{data}]" if data else ""
        print(f"  [M] {source} ▬▶ {target}{data_str}")

    @staticmethod
    def process_result(tool_name: str, result: str):
        """BPMN: Service task result received"""
        print(f"\n  ⬢ [SERVICE OUTPUT: {tool_name}]")
        print(f"  {'─'*66}")
        result_preview = str(result)[:700]
        if len(str(result)) > 700:
            result_preview += "\n  [...truncated...]"
        print(f"  {result_preview}")
        print(f"  {'─'*66}\n")

    @staticmethod
    def workflow_complete(status: str):
        """BPMN: Process completion"""
        print(f"  ● COMPLETE: {status}\n")

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
    before_after_data: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Before/After comparison. Format: {'parameter_name': {'before': value, 'after': value, 'unit': 'unit'}}")
    parts_replaced: List[Dict[str, str]] = Field(default_factory=list, description="Parts replaced. Format: [{'part': 'Part Name', 'torque_spec': '25 Nm', 'ima_code': 'IMA123'}]")
    cylinder_balance: Dict[str, float] = Field(default_factory=dict, description="Cylinder balance data for visualization. Format: {'Cylinder_1': 0.1, 'Cylinder_2': -0.2, ...}")

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
    BPMNLogger.header("Diagnostic Reasoning (Reasoner Task)")
    BPMNLogger.task_start("LLM Inference", "Initializing reasoning phase")
    
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

STEP 3 - ENHANCED REPORT SECTIONS:
For repair diagnostic reports, ALWAYS include:

A. BEFORE/AFTER COMPARISON (before_after_data):
   If faulty vs. repaired data is mentioned, create a comparison table:
   Example: {{"Fuel_Rail_Pressure": {{"before": "450 bar", "after": "280 bar", "unit": "bar"}}, "Injection_Correction": {{"before": "±0.5 mg/str", "after": "±0.2 mg/str", "unit": "mg/str"}}}}

B. PARTS REPLACED (parts_replaced):
   If any parts were repaired/replaced, list them with specifications:
   Example: [{{"part": "Fuel Injector #3", "torque_spec": "25 Nm", "ima_code": "IMA-INJ-0047"}}]

C. CYLINDER BALANCE DATA (cylinder_balance):
   If injection correction or cylinder-specific data exists, provide balance metrics:
   Example: {{"Cylinder_1": 0.1, "Cylinder_2": -0.2, "Cylinder_3": 0.15, "Cylinder_4": -0.05}}

STEP 4 - FORMATTING RULES:
- If the user asks for a repair procedure, put the sequential steps in the 'action_plan' array.
- If the user asks for a LIST OF TOOLS, PARTS, or TORQUE SPECS, put the list inside the 'diagnosis' string using Markdown bullet points. Leave 'action_plan' COMPLETELY EMPTY [].
- Output ONLY this JSON object (no other text):
{parser.get_format_instructions()}"""
    
    messages = [SystemMessage(content=agent_template)] + state['messages']
    response = llm_with_tools.invoke(messages)
    
    decision_entry = []
    if hasattr(response, 'tool_calls') and response.tool_calls:
        BPMNLogger.decision_point("Tool calls required", "Routing to Service Invocation")
        for t in response.tool_calls:
            BPMNLogger.service_invocation(t['name'], t['args'])
            decision_entry.append(f"REASONER ▬▶ SERVICE: {t['name']}")
    else:
        BPMNLogger.decision_point("Analysis complete", "Synthesizing final response")
        decision_entry.append("REASONER ▬▶ OUTPUT: Final Answer")
        
    return {"messages": [response], "decision_log": decision_entry}

def tool_logger_node(state: AgentState):
    """BPMN: Service Task Result Processing"""
    decision_entry = []
    last_msg = state['messages'][-1]
    if isinstance(last_msg, ToolMessage):
        tool_name = last_msg.name if hasattr(last_msg, 'name') and last_msg.name else "Tool"
        BPMNLogger.process_result(tool_name, last_msg.content)
        
        if 'predict_root_cause' in tool_name:
            BPMNLogger.data_flow("ML_CLASSIFIER", "REASONER", "Confidence Scores")
            decision_entry.append(f"ML_CLASSIFIER ▬▶ REASONER")
        elif 'vehicle_diagnostic_db' in tool_name:
            BPMNLogger.data_flow("RAG_DATABASE", "REASONER", "Knowledge Base Results")
            decision_entry.append(f"RAG_DATABASE ▬▶ REASONER")
        elif 'vehicle_web_search' in tool_name:
            BPMNLogger.data_flow("WEB_SEARCH", "REASONER", "External References")
            decision_entry.append(f"WEB_SEARCH ▬▶ REASONER")
            
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
# 5. BPMN PROCESS ORCHESTRATOR (WRAPPER)
# ==========================================
class BPMNProcessOrchestrator:
    """Orchestrates the diagnostic workflow with BPMN-compliant process tracking"""
    
    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        BPMNLogger.header("Diagnostic Session Initiated")
        BPMNLogger.task_start("Input Reception", inputs.get("input")[:80] + "...")
        
        result = langgraph_app.invoke({
            "messages": [HumanMessage(content=inputs.get("input", ""))], 
            "decision_log": []
        })
        
        final_content = result["messages"][-1].content
        decision_log = result.get("decision_log", [])
        
        BPMNLogger.header("Diagnostic Analysis Complete")
        BPMNLogger.task_start("Output Generation", "Formatting final diagnostic response")
        
        try:
            parsed = json.loads(final_content.replace("```json", "").replace("```", "").strip())
            BPMNLogger.data_flow("REASONER", "OUTPUT_FORMATTER", "Diagnostic_Response")
            print(json.dumps(parsed, indent=4))
        except:
            print(final_content)
        
        BPMNLogger.workflow_complete("Session concluded successfully")
        
        return {"output": final_content, "decision_log": decision_log}
    
    def get_graph(self):
        """Returns the executable workflow graph"""
        return langgraph_app.get_graph()

agent_executor = BPMNProcessOrchestrator()