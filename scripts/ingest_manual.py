import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# Configuration
PDF_PATH = "data/manuals/DTC_Codes.pdf"  # Ensure your PDF is in the data/ folder
COLLECTION_NAME = "vehicle_manuals_v2"

def ingest_manual():
    print(f"📄 Loading Manual: {PDF_PATH}...")
    
    # 1. Load the PDF
    if not os.path.exists(PDF_PATH):
        print(f"❌ Error: File not found at {PDF_PATH}")
        return

    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load()
    print(f"   Loaded {len(pages)} pages.")

    # 2. Split into Chunks (Critical for RAG)
    # We use a larger chunk size to keep "Symptom" and "Solution" together
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\nDTC", "\n\n", "\n", " "] # Try to split by DTC codes
    )
    splits = text_splitter.split_documents(pages)
    print(f"   Split into {len(splits)} chunks.")

    # 3. Connect to AstraDB
    print("🚀 Connecting to AstraDB...")
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    vstore = AstraDBVectorStore(
        embedding=embedding,
        collection_name=COLLECTION_NAME,
        api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
        token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
    )

    # 4. Insert Data
    print("💾 Uploading to Vector Store (this may take a moment)...")
    batch_size = 50
    for i in range(0, len(splits), batch_size):
        batch = splits[i:i+batch_size]
        vstore.add_documents(batch)
        print(f"   Processed batch {i} to {i+len(batch)}...")
        time.sleep(1) # Prevent rate limiting

    print("✅ Ingestion Complete! The 'Slow Brain' can now read the manual.")

if __name__ == "__main__":
    ingest_manual()
