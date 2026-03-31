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

# Fix gRPC DNS + SSL issues on macOS Python 3.13
import certifi
os.environ.setdefault('GRPC_DNS_RESOLVER', 'native')
os.environ.setdefault('SSL_CERT_FILE', certifi.where())
os.environ.setdefault('GRPC_DEFAULT_SSL_ROOTS_FILE_PATH', certifi.where())
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
        print(result[:800] + "..." if len(result) > 800 else result)
        print(f"{'-'*50}\n")

# ==========================================
# 2. OUTPUT SCHEMA & STATE
# ==========================================
class DiagnosticResponse(BaseModel):
    needs_more_info: bool
    clarifying_questions: List[str]
    diagnosis: str
    confidence_level: str = Field(description="Overall confidence as a label: High, Medium, or Low.")
    confidence_score: int = Field(description="Overall confidence as an integer percentage 0-100, e.g. 87.")
    rag_score: int = Field(description="Integer 0-100 reflecting how well the RAG knowledge base matched this case.")
    ml_score: int = Field(description="Integer 0-100 reflecting the ML classifier confidence for the predicted root cause.")
    web_score: int = Field(description="Integer 0-100 reflecting the quality/relevance of web search results. 80 if multiple relevant results, 40 if partial, 10 if none.")
    ml_evidence: str
    rag_evidence: str
    web_evidence: str
    action_plan: List[str]
    safety_warning: str

parser = PydanticOutputParser(pydantic_object=DiagnosticResponse)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    decision_log: Annotated[List[str], operator.add]

# ==========================================
# 3. NODES WITH ENHANCED LOGGING
# ==========================================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    google_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
)
tools = [predict_root_cause, vehicle_diagnostic_db, vehicle_web_search]
llm_with_tools = llm.bind_tools(tools)

def diagnostic_reasoner(state: AgentState):
    TerminalLogger.header("Agent Reasoning")
    
    agent_template = f"""You are a Master Diagnostic AI for vehicle troubleshooting.

STEP 1 - TOOLS: You MUST call predict_root_cause, vehicle_diagnostic_db, and vehicle_web_search before writing your final answer.

CRITICAL — predict_root_cause query format:
You MUST pass a JSON string with the EXACT numeric sensor values from the input. Do NOT paraphrase.
Extract these fields from the input and build the JSON:
  - "CAR_MODEL": vehicle model string (e.g. "Tata Nexon")
  - "ENGINE_RPM": RPM as a number
  - "VEHICLE_SPEED": speed in km/h as a number
  - "ENGINE_LOAD": engine load percentage as a number
  - "COOLANT_TEMP": temperature in Celsius as a number
  - "MAF_GRAMS_SEC": MAF in g/s as a number
  - "SHORT_TERM_TRIM": Short Term Trim percentage as a number
  - "LONG_TERM_TRIM": Long Term Trim percentage as a number
  - "THROTTLE_POS": Throttle Position percentage as a number
  - "DTC": the DTC code string if present (e.g. "P0171"), else omit

Example: {{"CAR_MODEL": "Tata Nexon", "ENGINE_RPM": 750, "VEHICLE_SPEED": 0, "ENGINE_LOAD": 30, "COOLANT_TEMP": 90, "MAF_GRAMS_SEC": 25, "SHORT_TERM_TRIM": 0, "LONG_TERM_TRIM": 0, "THROTTLE_POS": 20, "DTC": "P0171"}}

For vehicle_diagnostic_db and vehicle_web_search, write a natural language query including the DTC code and symptoms.

STEP 2 - SCORES: After running the tools, read the score hints they return:
- From predict_root_cause output → read 'ml_score_hint' (integer 0-100). Use this EXACTLY as ml_score.
  - If data_quality is 'LOW', subtract 15 from ml_score_hint.
- From vehicle_diagnostic_db output → read 'RAG_SCORE_HINT' (integer 0-100). Use this EXACTLY as rag_score.
  - If output says "No matching manual section found", set rag_score=5.
- confidence_score = MAXIMUM of (ml_score, rag_score, web_score). The overall confidence should reflect your strongest piece of evidence, do NOT average them.
- Web Search Score (web_score): Evaluate the string returned by vehicle_web_search.
  - 85-100: Results explicitly confirm the EXACT vehicle model & DTC with a clear common fix.
  - 50-70: Results discuss the DTC well, but for a different car OR the fix is debated.
  - 10-30: Generic SEO pages or barely relevant forum links.
  - 0: No results or tool failed.
- confidence_level = "High" if confidence_score >= 75, "Medium" if >= 50, "Low" otherwise.

STEP 3 - FORMAT: Output ONLY this JSON object (no other text):
{parser.get_format_instructions()}"""
    
    messages = [SystemMessage(content=agent_template)] + state['messages']
    response = llm_with_tools.invoke(messages)
    
    decision_entry = []
    if response.tool_calls:
        tool_names = [t['name'] for t in response.tool_calls]
        decision_entry.append(f"REASONER → Dispatching {len(tool_names)} tool(s): {', '.join(tool_names)}")
        for t in response.tool_calls:
            TerminalLogger.info("Action", f"Calling tool '{t['name']}' with args {t['args']}")
    else:
        decision_entry.append("REASONER → All evidence gathered, synthesizing final answer")
    
    return {"messages": [response], "decision_log": decision_entry}

def tool_logger_node(state: AgentState):
    decision_entry = []
    
    # Find the last AIMessage with tool_calls, then collect all ToolMessages after it
    ai_msg_idx = None
    for i in range(len(state['messages']) - 1, -1, -1):
        msg = state['messages'][i]
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            ai_msg_idx = i
            break
    
    if ai_msg_idx is None:
        return {"messages": [], "decision_log": decision_entry}
    
    ai_msg = state['messages'][ai_msg_idx]
    # Build map from tool_call_id → tool_name
    call_map = {tc['id']: tc['name'] for tc in ai_msg.tool_calls} if ai_msg.tool_calls else {}
    
    # Process all ToolMessages after the AIMessage
    for msg in state['messages'][ai_msg_idx + 1:]:
        if not isinstance(msg, ToolMessage):
            continue
        tool_name = call_map.get(getattr(msg, 'tool_call_id', ''), 'Unknown Tool')
        content = msg.content or ''
        TerminalLogger.tool_result(tool_name, content)
        
        if tool_name == 'predict_root_cause':
            try:
                result = json.loads(content)
                status = result.get('status', 'UNKNOWN')
                conf = result.get('confidence', 0)
                pred = result.get('prediction', '?')
                ml_hint = result.get('ml_score_hint', 0)
                quality = result.get('data_quality', 'UNKNOWN')
                quality_short = quality.split('—')[0].strip() if '—' in str(quality) else str(quality)
                decision_entry.append(
                    f"ML CLASSIFIER → Predicted: {pred} | Confidence: {conf*100:.0f}% | "
                    f"Status: {status} | Data Quality: {quality_short} | ML Score: {ml_hint}"
                )
                if status == 'UNCERTAIN':
                    decision_entry.append("ML DECISION → Low confidence, deeper RAG + web research triggered")
                else:
                    decision_entry.append("ML DECISION → High confidence, direct diagnosis identified")
            except Exception as e:
                decision_entry.append(f"ML CLASSIFIER → Output received (parse: {str(e)[:40]})")
        elif tool_name == 'vehicle_diagnostic_db':
            import re as _re
            rag_match = _re.search(r'RAG_SCORE_HINT:\s*(\d+)', content)
            rag_score = rag_match.group(1) if rag_match else '?'
            if 'No matching manual section found' in content:
                decision_entry.append(f"RAG DATABASE → No match found | RAG Score: 0")
            else:
                decision_entry.append(f"RAG DATABASE → Manual sections found | RAG Score: {rag_score}")
        elif tool_name == 'vehicle_web_search':
            try:
                results = json.loads(content)
                if isinstance(results, list):
                    n = len(results)
                    decision_entry.append(f"WEB SEARCH → {n} result(s) found")
                elif isinstance(results, dict) and 'error' in results:
                    decision_entry.append(f"WEB SEARCH → Error: {results['error'][:60]}")
                else:
                    decision_entry.append(f"WEB SEARCH → Results received")
            except Exception:
                decision_entry.append(f"WEB SEARCH → Results received")
        else:
            decision_entry.append(f"TOOL: {tool_name} → Executed")
    
    return {"messages": [], "decision_log": decision_entry}

# ==========================================
# 4. GRAPH CONSTRUCTION
# ==========================================
def _route_reasoner(state: AgentState) -> str:
    """Router: decide whether to call tools or finish."""
    last_msg = state['messages'][-1]
    if last_msg.tool_calls:
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