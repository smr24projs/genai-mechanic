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
# store = {}

# def get_session_history(session_id: str) -> BaseChatMessageHistory:
#     if session_id not in store:
#         store[session_id] = ChatMessageHistory()
#     return store[session_id]

# # --- CRASH GUARD FUNCTION ---
# def handle_parsing_errors(error) -> str:
#     """
#     This function catches the 'Name cannot be empty' error.
#     Instead of crashing, it returns a message saying the tool failed but lets the chat continue.
#     """
#     return f"⚠️ System Warning: A tool returned an invalid format ({str(error)}). I will try to answer based on what I know."

# def build_advisor_agent():
#     api_key = os.getenv("GOOGLE_API_KEY")
#     if not api_key: return None

#     # Safety Settings
#     safety_settings = {
#         HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
#     }

#     # Model
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

#     # Prompt
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """You are an expert AI Master Mechanic. 
        
#         **Your Goal:** Diagnose vehicle issues using your tools.
        
#         **Rules:**
#         1. If a Web Search fails or returns an error, do NOT crash. Just say "I couldn't verify this online."
#         2. ALWAYS confirm the Vehicle Year, Make, and Model.
#         3. If you find multiple potential causes, list them in order of likelihood.
#         """),
#         ("placeholder", "{chat_history}"),
#         ("human", "{input}"),
#         ("placeholder", "{agent_scratchpad}"),
#     ])

#     agent = create_tool_calling_agent(llm, tools, prompt)
    
#     agent_executor = AgentExecutor(
#         agent=agent, 
#         tools=tools, 
#         verbose=True,
#         # THIS IS THE KEY FIX:
#         handle_parsing_errors=handle_parsing_errors
#     )

#     return RunnableWithMessageHistory(
#         agent_executor,
#         get_session_history,
#         input_messages_key="input",
#         history_messages_key="chat_history",
#     )




# # src/agents/advisor.py
# import os
# from dotenv import load_dotenv

# # LangChain Imports
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.agents import AgentExecutor, create_tool_calling_agent
# from langchain_core.prompts import ChatPromptTemplate

# # Import your Custom Tools
# # Ensure these files exist in src/tools/ based on previous steps
# from src.tools.vehicle_rag_tool import vehicle_diagnostic_db  # Your existing RAG tool
# from src.tools.web_search import vehicle_web_search          # New Ranked Search
# from src.tools.classifier_tool import predict_root_cause     # New ML Classifier

# # Load Environment Variables
# load_dotenv()

# # 1. Initialize the LLM (Gemini 2.5 Flash)
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0.3,  # Low temp for factual accuracy
#     api_key=os.getenv("GOOGLE_API_KEY")
# )

# # 2. Define the System Prompt ("AI Mechanic Persona")
# SYSTEM_PROMPT = """
# You are a Senior Diagnostic Judge. You must compare the ML Model's guess against the top Web Search results.

# ### PHASE 1: EVALUATE ML MODEL
# - Report the ML Confidence score from 'predict_root_cause'.

# ### PHASE 2: RANK WEBSITES
# - From the web search tool, identify the TOP 3 most relevant websites.
# - For each, list: [Rank] Website Name | Confidence Score | Source Type.
# - **Authority Bonus**: Add +5% to the score if the site is an official manufacturer domain (.ford.com, .tata.com) or a highly trusted forum (Team-BHP, Reddit r/MechanicAdvice).

# ### PHASE 3: FINAL CONSENSUS
# - Identify the 'Best Web Confidence' (the highest score from your top 3).
# - Compare ML Confidence vs. Best Web Confidence.
# - State the winner and provide the Final Diagnosis based on the winning data.

# ### REQUIRED OUTPUT FORMAT:
# 1. **ML Analysis**: [Score]%
# 2. **Web Ranking**:
#    - 1st: [Site Name] ([Score]%)
#    - 2nd: [Site Name] ([Score]%)
#    - 3rd: [Site Name] ([Score]%)
# 3. **Verdict**: [ML or Web] wins with [Score]%.
# 4. **Final Diagnosis**: [Root Cause]
# 5. **Action Plan**: [Steps...]
# """

# prompt = ChatPromptTemplate.from_messages([
#     ("system", SYSTEM_PROMPT),
#     ("human", "{input}"),
#     ("placeholder", "{agent_scratchpad}"),
# ])

# # 3. Register Tools
# tools = [
#     predict_root_cause,     # The ML Model
#     vehicle_diagnostic_db,  # The Vector DB (RAG)
#     vehicle_web_search      # The Ranked Web Search
# ]

# # 4. Create the Agent
# agent = create_tool_calling_agent(llm, tools, prompt)

# # 5. Create the Executor (This is what app.py imports)
# agent_executor = AgentExecutor(
#     agent=agent,
#     tools=tools,
#     verbose=True,            # Prints thinking process to console
#     handle_parsing_errors=True
# )



# import os
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.agents import create_tool_calling_agent, AgentExecutor
# from langchain_core.prompts import ChatPromptTemplate

# # --- IMPORT TOOLS ---
# from src.tools.classifier_tool import predict_root_cause
# from src.tools.web_search import vehicle_web_search
# # 👇 THIS IMPORT WAS MISSING OR COMMENTED OUT
# from src.tools.rag_tool import vehicle_diagnostic_db 

# load_dotenv()

# # --- CRASH GUARD ---
# def handle_parsing_errors(error) -> str:
#     return f"⚠️ System Warning: Tool output format error ({str(error)}). Proceeding with internal reasoning."

# SYSTEM_PROMPT = """
# You are the Senior AI Vehicle Diagnostic Judge. You analyze Diagnostic Trouble Codes (DTC) 
# and mechanical symptoms using a three-tier consensus system.

# ### Tier 1: ML CLASSIFICATION (XGBoost)
# - Start by calling 'predict_root_cause'.
# - Confidence >= 70%: This is your primary lead.
# - Confidence < 70%: Move to Tier 2 research.

# ### Tier 2: RANKED RESEARCH (Tavily & RAG)
# - Use 'vehicle_diagnostic_db' to check the Official Manual for 'Possible Causes' and specs.
# - Use 'vehicle_web_search' to find TSBs and forums.
# - **Authority Bonus**: Add +5% to the score for 'Team-BHP' or official manufacturer domains.

# ### Tier 3: THE VERDICT
# - Compare ML Score vs. Web/RAG Confidence.
# - State which system "won" and why.
# - Provide a 3-step Action Plan: Safety, Verification, and Repair.

# REQUIRED OUTPUT FORMAT:
# 1. **ML Analysis**: [Score]%
# 2. **Web Ranking**: [Top 3 sources]
# 3. **Verdict**: [Winner] wins with [Score]%
# 4. **Final Diagnosis**: [Root Cause]
# 5. **Action Plan**: [Steps]
# """

# def build_advisor():
#     # Initialize Gemini 3 Flash
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash", 
#         temperature=0
#     )

#     prompt = ChatPromptTemplate.from_messages([
#         ("system", SYSTEM_PROMPT),
#         ("human", "{input}"),
#         ("placeholder", "{agent_scratchpad}"),
#     ])

#     # Register ALL tools
#     tools = [
#         predict_root_cause,     # Tier 1: XGBoost
#         vehicle_web_search,     # Tier 2: Web Search
#         vehicle_diagnostic_db   # Tier 2: Official Manual (RAG)
#     ]

#     agent = create_tool_calling_agent(llm, tools, prompt)
    
#     return AgentExecutor(
#         agent=agent, 
#         tools=tools, 
#         verbose=True, 
#         handle_parsing_errors=handle_parsing_errors
#     )

# # --- GLOBAL INSTANCE ---
# agent_executor = build_advisor()



import os
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel, Field, validator
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI

# Import your custom tools
from src.tools.classifier_tool import predict_root_cause
from src.tools.rag_tool import vehicle_diagnostic_db
from src.tools.web_search import vehicle_web_search

load_dotenv()

# ==========================================
# 1. DEFINE THE STRICT VALIDATION SCHEMA
# ==========================================
class DiagnosticResponse(BaseModel):
    # --- CLARIFICATION FIELDS ---
    needs_more_info: bool = Field(description="Set to True ONLY IF the user prompt is too vague (no DTCs, no sensor data, generic complaint). False otherwise.")
    clarifying_questions: List[str] = Field(description="If needs_more_info is True, list 1-3 specific questions to ask the mechanic. Else empty list.")
    
    # --- EXISTING DIAGNOSTIC FIELDS ---
    diagnosis: str = Field(description="The final diagnosis. Write 'Pending' if needs_more_info is True.")
    confidence_level: str = Field(description="High, Medium, or Low. Write 'None' if needs_more_info is True.")
    ml_evidence: str = Field(description="Summary of ML findings. Write 'None' if not used.")
    rag_evidence: str = Field(description="Summary of RAG findings. Write 'None' if not used.")
    web_evidence: str = Field(description="Summary of Web findings. Write 'None' if not used.")
    action_plan: List[str] = Field(description="Step-by-step repair instructions. If needs_more_info is True, return ['Pending'].")
    safety_warning: str = Field(description="Any critical safety warnings. If none, write 'None'.")

    # Logical Cross-Check Validation
    @validator('action_plan')
    def validate_action_plan_sources(cls, action_plan, values):
        """Ensures the LLM doesn't hallucinate an action plan without evidence."""
        
        # BYPASS: If the AI just needs more info, skip the strict evidence validation
        if values.get('needs_more_info') is True:
            return action_plan
            
        ml = values.get('ml_evidence', 'None')
        rag = values.get('rag_evidence', 'None')
        web = values.get('web_evidence', 'None')
        
        if ml == 'None' and rag == 'None' and web == 'None':
            raise ValueError("Validation Failed: Action plan generated without citing any tool evidence.")
        
        if len(action_plan) == 0:
            raise ValueError("Validation Failed: Action plan cannot be empty.")
            
        return action_plan

# Initialize the Parser
parser = PydanticOutputParser(pydantic_object=DiagnosticResponse)

# ==========================================
# 2. INITIALIZE THE LLM & TOOLS
# ==========================================
# Using the stable Gemini 2.5 Flash model as requested
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

# List of tools the agent can use
tools = [predict_root_cause, vehicle_diagnostic_db, vehicle_web_search]

# ==========================================
# 3. BUILD THE PROMPT TEMPLATE
# ==========================================
agent_template = """
You are a Master Diagnostic Technician AI designed for COMPLEX vehicle troubleshooting.
You are assisting a professional mechanic. Do not give basic, consumer-level advice (like "check the gas cap").

Use your ML, RAG, and Web Search tools to find deep, technical root causes such as:
- Wiring harness chafing or pin-fitment issues.
- Corrupted module communications (U-codes).
- Subtle sensor biases (e.g., O2 sensors stuck lean, MAP sensor skewed).
- Complex mechanical failures (e.g., VVT phaser failure, DPF blockage, internal transmission leaks).

Analyze the mechanic's provided UI Selections, DTCs, and live data to formulate a comprehensive verdict.

CRITICAL INSTRUCTION: You MUST format your FINAL output exactly according to these rules:
{format_instructions}
Do not include any conversational text outside of the JSON block in your final answer.

User Query: {input}
{agent_scratchpad}
"""

prompt = PromptTemplate(
    template=agent_template,
    input_variables=["input", "agent_scratchpad"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# ==========================================
# 4. CREATE THE AGENT EXECUTOR
# ==========================================
agent = create_tool_calling_agent(llm, tools, prompt)

# The AgentExecutor handles the actual running and tool invoking
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True,
    max_iterations=5 # Prevents infinite loops
)