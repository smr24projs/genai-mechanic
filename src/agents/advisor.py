# import os
# from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
# from langchain.agents import create_tool_calling_agent, AgentExecutor
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_core.chat_history import BaseChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory

# # Import Tools
# from src.tools.web_scraper import get_web_scraper_tool
# from src.tools.mcp_tool import get_mcp_tool
# from src.rag.retriever import get_rag_tool
# from src.tools.vision_tool import get_vision_tool

# # --- MEMORY STORAGE ---
# # In a real app, use Redis or a database. For now, in-memory dictionary is fine.
# store = {}

# def get_session_history(session_id: str) -> BaseChatMessageHistory:
#     if session_id not in store:
#         store[session_id] = ChatMessageHistory()
#     return store[session_id]

# def build_advisor_agent():
#     api_key = os.getenv("GOOGLE_API_KEY")
#     if not api_key:
#         return None

#     # Safety Settings
#     safety_settings = {
#         HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
#     }

#     # Model (Gemini 1.5 Flash for speed & quota)
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash", 
#         temperature=0,
#         google_api_key=api_key,
#         safety_settings=safety_settings
#     )

#     # Tools
#     tools = [
#         get_rag_tool(),
#         get_web_scraper_tool(),
#         get_mcp_tool(),
#         get_vision_tool()
#     ]

#     # Prompt with Memory Placeholder
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", "You are an expert vehicle mechanic advisor. "
#                    "Use 'vehicle_diagnostic_db' for official manual lookups. "
#                    "Use 'web_search' for recent recalls, news, or forum advice. "
#                    "Use 'read_local_file' to read service logs. "
#                    "Use 'vision_analysis' if the user asks you to look at an image path. "
#                    "If the user asks about recalls for a 2024+ vehicle, ALWAYS use web_search. "
#                    "Always consider the chat history for context (e.g. vehicle year/make/model)."),
#         ("placeholder", "{chat_history}"), # <--- MEMORY INJECTED HERE
#         ("human", "{input}"),
#         ("placeholder", "{agent_scratchpad}"),
#     ])

#     agent = create_tool_calling_agent(llm, tools, prompt)
    
#     agent_executor = AgentExecutor(
#         agent=agent, 
#         tools=tools, 
#         verbose=True,
#         handle_parsing_errors=True
#     )

#     # Wrap Agent with Automatic Memory Management
#     agent_with_history = RunnableWithMessageHistory(
#         agent_executor,
#         get_session_history,
#         input_messages_key="input",
#         history_messages_key="chat_history",
#     )
    
#     return agent_with_history


import os
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain.agents import create_tool_calling_agent, AgentExecutor
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

# --- CRASH GUARD FUNCTION ---
def handle_parsing_errors(error) -> str:
    """
    This function catches the 'Name cannot be empty' error.
    Instead of crashing, it returns a message saying the tool failed but lets the chat continue.
    """
    return f"⚠️ System Warning: A tool returned an invalid format ({str(error)}). I will try to answer based on what I know."

def build_advisor_agent():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return None

    # Safety Settings
    safety_settings = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    }

    # Model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0,
        google_api_key=api_key,
        safety_settings=safety_settings
    )

    # Tools
    tools = [
        get_rag_tool(),
        get_web_scraper_tool(),
        get_mcp_tool(),
        get_vision_tool()
    ]

    # Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI Master Mechanic. 
        
        **Your Goal:** Diagnose vehicle issues using your tools.
        
        **Rules:**
        1. If a Web Search fails or returns an error, do NOT crash. Just say "I couldn't verify this online."
        2. ALWAYS confirm the Vehicle Year, Make, and Model.
        3. If you find multiple potential causes, list them in order of likelihood.
        """),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        # THIS IS THE KEY FIX:
        handle_parsing_errors=handle_parsing_errors
    )

    return RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )