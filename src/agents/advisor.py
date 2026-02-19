import os
from src.tools.diagnostics import get_ml_diagnostic_tool
from src.tools.dtc_classifier import get_dtc_cascade_tool
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
# --- FIXED IMPORTS FOR LANGCHAIN 0.3 ---
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.tools import format_to_tool_messages
from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
# ---------------------------------------
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Import Tools
from src.tools.web_scraper import get_web_scraper_tool
from src.tools.mcp_tool import get_mcp_tool
from src.rag.retriever import get_rag_tool
from src.tools.vision_tool import get_vision_tool

# --- MEMORY STORAGE ---
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def handle_parsing_errors(error) -> str:
    return f"⚠️ System Warning: A tool returned an invalid format ({str(error)}). I will try to answer based on what I know."

def build_advisor_agent():
    # Use the correct key name from your .env file
    api_key = os.getenv("GEMINI_API_KEY") 
    if not api_key: 
        return None

    # Safety Settings [cite: 83]
    safety_settings = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    }

    # Model: Updated from 2.5 to 1.5 
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0,
        google_api_key=api_key,
        safety_settings=safety_settings
    )

    # Tools [cite: 21, 56]
    tools = [
        get_dtc_cascade_tool(),  # ML → RAG → Web Scraper cascade
        get_rag_tool(),
        get_web_scraper_tool(),
        get_mcp_tool(),
        get_vision_tool()
    ]

    # Prompt [cite: 79, 80]
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI Master Mechanic. 
        
        **Your Goal:** Diagnose vehicle issues using your tools. [cite: 13, 42]
        
        **Rules:**
        1. If a Web Search fails, do NOT crash. Just say "I couldn't verify this online."
        2. ALWAYS confirm the Vehicle Year, Make, and Model. [cite: 43]
        3. If you find multiple potential causes, list them in order of likelihood. [cite: 44]
        4. **IMPORTANT:** When sensor data is provided, ALWAYS use the `dtc_cascade_diagnostic` tool first.
           It runs an ML model (Random Forest) with confidence scoring, and automatically falls back to 
           RAG (AstraDB manuals) and Web Search if needed.
        5. In your response, ALWAYS display:
           - The **DTC Prediction** (e.g., P0300)
           - The **Confidence Score** (e.g., 85.2%)
           - The **Source** used (ML Model / RAG / Web Search)
           - The **Cascade Path** showing which sources were tried
        6. Parse the JSON returned by the cascade tool and present it in a clear, readable format.
        """),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # Modern LCEL Agent Construction
    llm_with_tools = llm.bind_tools(tools)
    
    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_tool_messages(x["intermediate_steps"]),
            "chat_history": lambda x: x.get("chat_history", []),
        }
        | prompt
        | llm_with_tools
        | ToolsAgentOutputParser()
    )
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=handle_parsing_errors
    )

    return RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )