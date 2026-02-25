import os

# --- 1. Fix src/tools/web_search.py ---
web_search_code = """import os
import json
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

# Initialize Tavily
tavily_tool = TavilySearchResults(max_results=5)

@tool
def vehicle_web_search(query: str):
    \"\"\"
    Search the web for real-time vehicle diagnostic data, TSBs, and forums.
    \"\"\"
    try:
        results = tavily_tool.run(query)
        # CRITICAL FIX: Convert List to JSON String to satisfy Gemini's output requirements
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})
"""

# --- 2. Fix src/tools/rag_tool.py ---
rag_tool_code = """import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# Configuration
COLLECTION_NAME = "vehicle_manuals_v2" 
EMBEDDING_MODEL = "models/text-embedding-004" 

# Initialize Embedding & DB
embedding = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
vstore = AstraDBVectorStore(
    embedding=embedding,
    collection_name=COLLECTION_NAME,
    api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
    token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
)

@tool
def vehicle_diagnostic_db(query: str):
    \"\"\"
    Query the official Vehicle Service Manual (PDF) for technical specifications,
    wiring diagrams, and official 'Possible Causes' for DTC codes.
    \"\"\"
    try:
        results = vstore.similarity_search(query, k=4)
        context = "\\n\\n".join([doc.page_content for doc in results])
        
        if not context:
            return "No specific manual section found for this query."
            
        return f"OFFICIAL MANUAL EXTRACT:\\n{context}"
        
    except Exception as e:
        return f"RAG Error: {str(e)}"
"""

# --- Write Files ---
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Fixed {path}")

write_file("src/tools/web_search.py", web_search_code)
write_file("src/tools/rag_tool.py", rag_tool_code)
print("\\n🚀 All tools patched! Please restart 'streamlit run app.py' now.")
