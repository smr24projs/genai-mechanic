import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from langchain.tools.retriever import create_retriever_tool

load_dotenv()

# TRY THIS EXACT STRING:
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# If that still gives 404, it means Google has fully turned off that model for your API key tier.
# You MUST switch to "models/text-embedding-004" and re-ingest your data.

vstore = AstraDBVectorStore(
    collection_name="vehicle_manuals_v2",
    embedding=embeddings,
    api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
    token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
)

retriever = vstore.as_retriever(search_kwargs={"k": 3})

vehicle_diagnostic_db = create_retriever_tool(
    retriever,
    name="vehicle_diagnostic_db",
    description="Searches for official vehicle manual information. Use this tool FIRST for specific technical data."
)
