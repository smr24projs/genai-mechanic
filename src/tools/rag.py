import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from langchain.tools.retriever import create_retriever_tool

# Load environment variables
load_dotenv()

# 1. Setup Embeddings
# This MUST match the model you used to upload the PDFs originally.
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# 2. Connect to AstraDB
# Ensure ASTRA_DB_API_ENDPOINT and ASTRA_DB_APPLICATION_TOKEN are in your .env file
vstore = AstraDBVectorStore(
    collection_name="vehicle_manuals",  # CHECK: Is this your actual collection name in AstraDB?
    embedding=embeddings,
    api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
    token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
)

# 3. Create the Retriever
retriever = vstore.as_retriever(search_kwargs={"k": 3})

# 4. Create the Tool
# This variable 'vehicle_diagnostic_db' is what advisor.py is trying to import
vehicle_diagnostic_db = create_retriever_tool(
    retriever,
    name="vehicle_diagnostic_db",
    description="Searches for official vehicle manual information, including torque specs, wiring diagrams, and diagnostic procedures. Use this tool FIRST for specific technical data."
)
