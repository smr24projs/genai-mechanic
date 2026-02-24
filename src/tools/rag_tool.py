import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# Configuration
COLLECTION_NAME = "vehicle_manuals_v2" 
EMBEDDING_MODEL = "models/gemini-embedding-001" 

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
    """
    Query the official Vehicle Service Manual (PDF) for technical specifications,
    wiring diagrams, and official 'Possible Causes' for DTC codes.
    """
    try:
        results = vstore.similarity_search(query, k=4)
        context = "\n\n".join([doc.page_content for doc in results])
        
        if not context:
            return "No specific manual section found for this query."
            
        return f"OFFICIAL MANUAL EXTRACT:\n{context}"
        
    except Exception as e:
        return f"RAG Error: {str(e)}"
