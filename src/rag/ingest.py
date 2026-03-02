import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# Verify Keys
if not os.getenv("ASTRA_DB_APPLICATION_TOKEN"):
    raise ValueError("❌ ERROR: ASTRA_DB_APPLICATION_TOKEN not found in .env")
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("❌ ERROR: GOOGLE_API_KEY not found in .env")

def ingest_manuals():
    print("🚀 Starting Ingestion Process...")
    
    # 1. Setup Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    # 2. Connect to AstraDB
    collection_name = os.getenv("ASTRA_DB_COLLECTION") or "vehicle_manuals"
    print(f"   - Connecting to AstraDB collection: {collection_name}...")
    
    vector_store = AstraDBVectorStore(
        collection_name=collection_name,
        embedding=embeddings,
        api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
        token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
    )

    # 3. Load the PDF — use path relative to this script's location
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "manuals", "DTC_Codes.pdf")
    pdf_path = os.path.abspath(pdf_path)
    
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: File not found at {pdf_path}")
        return


    print(f"   - Loading file: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    print(f"   - Loaded {len(pages)} pages.")

    # 4. Split Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(pages)
    total_splits = len(splits)
    print(f"   - Split into {total_splits} chunks.")

    # 5. Upload in Batches (To avoid Rate Limits)
    BATCH_SIZE = 20  # Safe number for Free Tier
    print(f"   - Uploading in batches of {BATCH_SIZE}...")

    for i in range(0, total_splits, BATCH_SIZE):
        batch = splits[i : i + BATCH_SIZE]
        print(f"     Processing batch {i} to {i + len(batch)}...")
        
        try:
            vector_store.add_documents(batch)
            # Small pause to be nice to the API
            time.sleep(2) 
        except Exception as e:
            if "429" in str(e):
                print("     ⚠️  Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                # Retry the batch
                vector_store.add_documents(batch)
            else:
                print(f"     ❌ Error on batch {i}: {e}")

    print("✅ Ingestion Complete! Your PDF is now searchable.")

if __name__ == "__main__":
    ingest_manuals()
