# import os
# from dotenv import load_dotenv
# from langchain_core.tools import StructuredTool
# from pydantic import BaseModel, Field
# from langchain_astradb import AstraDBVectorStore
# from langchain_google_genai import GoogleGenerativeAIEmbeddings

# load_dotenv()

# # 1. Input Schema
# class DiagnosticInput(BaseModel):
#     query: str = Field(description="The diagnostic code (e.g., 'P0300') or specific vehicle issue to look up.")

# # 2. Setup Retrieval Logic
# try:
#     # UPDATED MODEL NAME HERE TOO:
#     embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
#     vector_store = AstraDBVectorStore(
#         collection_name=os.getenv("ASTRA_DB_COLLECTION", "vehicle_manuals_v2"),
#         embedding=embeddings,
#         api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
#         token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
#     )
#     retriever = vector_store.as_retriever(search_kwargs={"k": 3})
# except Exception as e:
#     print(f"Warning: AstraDB not connected. RAG will fail. Error: {e}")
#     retriever = None

# def query_vector_db(query: str):
#     if not retriever:
#         return "Error: Database connection failed. Check your .env file."
    
#     print(f"\n[DEBUG] Searching AstraDB for: {query}")
    
#     try:
#         results = retriever.invoke(query)
#         if not results:
#             return "No relevant information found in the service manuals."
        
#         context_text = "\n\n".join([f"Source: {doc.page_content}" for doc in results])
#         return f"Found the following info in manuals:\n{context_text}"
#     except Exception as e:
#         return f"Error querying database: {str(e)}"

# # 3. Tool Definition
# def get_rag_tool():
#     return StructuredTool.from_function(
#         func=query_vector_db,
#         name="vehicle_diagnostic_db",
#         description="Use this tool to look up official factory service manual data, DTC codes, and repair procedures.",
#         args_schema=DiagnosticInput
#     )



# import os
# from langchain_community.vectorstores import AstraDB
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_core.tools import StructuredTool
# from pydantic import BaseModel, Field

# # 1. Connect to AstraDB
# def get_vectorstore():
#     api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
#     token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    
#     if not api_endpoint or not token:
#         return None

#     embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
#     return AstraDB(
#         embedding=embeddings,
#         collection_name="vehicle_manuals_v2",
#         api_endpoint=api_endpoint,
#         token=token,
#     )

# # 2. Input Schema
# class RAGInput(BaseModel):
#     query: str = Field(description="The diagnostic query (e.g., 'P0300 causes' or 'oil capacity').")

# # 3. The Tool Function
# def query_manuals(query: str) -> str:
#     """
#     Searches the vehicle service manuals for the given query.
#     Returns the relevant text segments as a single string.
#     """
#     try:
#         print(f"\n[DEBUG] Searching AstraDB for: {query}")
#         vstore = get_vectorstore()
#         if not vstore:
#             return "Error: Database connection failed. Check .env variables."

#         # Perform Search
#         results = vstore.similarity_search(query, k=4)
        
#         if not results:
#             return "No relevant information found in the uploaded manuals."

#         # FIX: Convert the list of Documents into a single clean string
#         # This prevents the 'Name cannot be empty' error in the Gemini API
#         formatted_response = "Found the following info in manuals:\n"
#         for i, doc in enumerate(results):
#             content = doc.page_content.replace("\n", " ") # Remove messy line breaks
#             formatted_response += f"--- Result {i+1} ---\n{content}\n\n"
            
#         return formatted_response

#     except Exception as e:
#         return f"Error querying database: {str(e)}"

# # 4. Create the Tool
# def get_rag_tool():
#     return StructuredTool.from_function(
#         func=query_manuals,
#         name="vehicle_diagnostic_db",
#         description="Searches official service manuals. Use this for codes, torque specs, and wiring.",
#         args_schema=RAGInput
#     )


import os
from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

# 1. Connect to AstraDB with Gemini Embeddings
def get_vectorstore():
    # Load credentials from .env
    api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
    token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    collection = os.getenv("ASTRA_DB_COLLECTION", "vehicle_manuals_v2") # Default to v2 if missing
    
    if not api_endpoint or not token:
        print("❌ Error: Missing AstraDB credentials in .env")
        return None

    # SPECIFIC UPDATE: Use "models/gemini-embedding-001"
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # Connect to the Vector Store using the modern class
    return AstraDBVectorStore(
        embedding=embeddings,
        collection_name=collection,
        api_endpoint=api_endpoint,
        token=token,
    )

# 2. Input Schema for the Tool
class RAGInput(BaseModel):
    query: str = Field(description="The diagnostic query (e.g., 'P0300 causes' or 'oil capacity').")

# 3. The Search Logic
def query_manuals(query: str) -> str:
    """
    Searches the vehicle service manuals for the given query.
    Returns the relevant text segments as a single string.
    """
    try:
        print(f"\n[DEBUG] Searching AstraDB for: {query}")
        vstore = get_vectorstore()
        if not vstore:
            return "Error: Database connection failed. Check .env variables."

        # Perform Similarity Search (Top 4 results)
        results = vstore.similarity_search(query, k=4)
        
        if not results:
            return "No relevant information found in the uploaded manuals."

        # Format results into a clean string for the Agent
        formatted_response = "Found the following info in manuals:\n"
        for i, doc in enumerate(results):
            # Clean up newlines to make it easier for the LLM to read
            content = doc.page_content.replace("\n", " ") 
            formatted_response += f"--- Result {i+1} ---\n{content}\n\n"
            
        return formatted_response

    except Exception as e:
        return f"Error querying database: {str(e)}"

# 4. Export the Tool
def get_rag_tool():
    return StructuredTool.from_function(
        func=query_manuals,
        name="vehicle_diagnostic_db",
        description="Searches official service manuals. Use this for specific codes, torque specs, and wiring diagrams.",
        args_schema=RAGInput
    )
