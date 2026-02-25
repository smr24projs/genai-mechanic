import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from astrapy.db import AstraDB

load_dotenv()

# --- CONFIGURATION ---
PDF_PATH = "data/DTC_Codes.pdf"
COLLECTION_NAME = "vehicle_manuals_final" # New clean collection
EMBEDDING_MODEL = "models/gemini-embedding-001"    # STABLE MODEL (768 dims)

def reset_and_ingest():
    print(f"🧹 Starting Reset for Collection: {COLLECTION_NAME}")
    
    # 1. Initialize Stable Embedding Model
    embedding = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    
    # 2. Hard Reset: Delete existing collection if it exists
    try:
        db = AstraDB(
            token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
            api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT")
        )
        db.delete_collection(COLLECTION_NAME)
        print("   ✅ Old collection deleted (if existed).")
    except Exception as e:
        print(f"   ℹ️  Collection clean (or error ignored): {e}")

    # 3. Create Fresh Vector Store
    print(f"   Creating new collection with '{EMBEDDING_MODEL}'...")
    vstore = AstraDBVectorStore(
        embedding=embedding,
        collection_name=COLLECTION_NAME,
        api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
        token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
    )

    # 4. Load & Split PDF
    if not os.path.exists(PDF_PATH):
        print(f"❌ Error: {PDF_PATH} not found.")
        return

    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200, 
        separators=["\n\nDTC", "\n\n", "\n", " "]
    )
    splits = text_splitter.split_documents(pages)
    print(f"   Prepared {len(splits)} chunks.")

    # 5. Upload
    print("🚀 Uploading to AstraDB...")
    batch_size = 50
    for i in range(0, len(splits), batch_size):
        batch = splits[i:i+batch_size]
        vstore.add_documents(batch)
        print(f"   Uploaded batch {i} - {i+len(batch)}")
        time.sleep(1)

    print("✅ Ingestion Complete! RAG is ready.")

if __name__ == "__main__":
    reset_and_ingest()
