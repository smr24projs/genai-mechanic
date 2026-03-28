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