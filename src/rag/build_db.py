import os
import getpass
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def build_database():
    # --- CRITICAL FIX: FORCE API KEY USAGE ---
    # 1. Get the key (Looking for GEMINI_API_KEY now)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY not found in .env file.")

    # 2. Force the library to ignore system 'gcloud' credentials
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

    print(f"🔑 Using API Key starting with: {api_key[:5]}...")

    # 3. Setup Embeddings
    # Note: The library parameter is still called 'google_api_key', 
    # but we pass your 'GEMINI_API_KEY' value into it.
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", 
        google_api_key=api_key
    )
    # -----------------------------------------

    print("🔄 Loading Service Manuals...")
    
    manual_path = "data/manuals/service_manual_dummy.txt"
    if not os.path.exists(manual_path):
        print(f"❌ Error: {manual_path} not found.")
        return

    loader = TextLoader(manual_path)
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    print(f"📄 Split manual into {len(chunks)} chunks.")

    db_path = "./data/chroma_db"
    
    # Create the vector store
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_path
    )
    print(f"✅ Database built successfully at {db_path}")

if __name__ == "__main__":
    build_database()
