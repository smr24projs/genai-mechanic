import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

COLLECTION_NAME = "vehicle_manuals"   # vehicle_manuals_v2 was empty; data is in vehicle_manuals
EMBEDDING_MODEL = "models/gemini-embedding-001"

# Lazy initialization — connect on first use
_vstore = None

def _get_vstore():
    global _vstore
    if _vstore is None:
        embedding = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        _vstore = AstraDBVectorStore(
            embedding=embedding,
            collection_name=COLLECTION_NAME,
            api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
            token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
        )
    return _vstore


@tool
def vehicle_diagnostic_db(query: str) -> str:
    """
    Query the official Vehicle Service Manual database for technical specifications,
    wiring diagrams, and official 'Possible Causes' for DTC codes.
    Returns the manual excerpt AND a relevance score (0.0 to 1.0).

    CRITICAL: The 'rag_score_hint' in the output is the actual cosine similarity score
    from the vector database (converted to 0-100). Use it directly as the rag_score
    in your final response JSON. Do NOT invent a different number.
    """
    try:
        vstore = _get_vstore()

        # Use similarity_search_with_score to get actual cosine similarity scores
        results_with_scores = vstore.similarity_search_with_score(query, k=4)

        if not results_with_scores:
            return (
                "RAG_RESULT: No matching manual section found.\n"
                "RAG_SCORE_HINT: 0\n"
                "Use rag_score=0 in your response."
            )

        # Build context with individual scores
        context_parts = []
        scores = []
        for doc, score in results_with_scores:
            # AstraDB returns a distance score (lower = more similar for L2, higher for cosine)
            # Cosine similarity is already 0-1 where 1 = perfect match
            similarity = round(float(score), 4)
            scores.append(similarity)
            context_parts.append(
                f"[Relevance: {similarity:.2f}]\n{doc.page_content[:600]}"
            )

        # Use the best (highest) similarity score as the RAG score
        best_score = max(scores)
        avg_score = sum(scores) / len(scores)

        # Convert to 0-100 integer for the LLM
        rag_score_hint = round(best_score * 100)

        context_text = "\n\n---\n\n".join(context_parts)

        return (
            f"OFFICIAL MANUAL EXTRACT (Top {len(results_with_scores)} results):\n\n"
            f"{context_text}\n\n"
            f"---\n"
            f"RAG_SCORE_HINT: {rag_score_hint}\n"
            f"Best similarity: {best_score:.3f} | Avg similarity: {avg_score:.3f}\n"
            f"Use rag_score={rag_score_hint} in your final response JSON."
        )

    except Exception as e:
        return (
            f"RAG Error: {str(e)}\n"
            f"RAG_SCORE_HINT: 0\n"
            f"Use rag_score=0 in your response."
        )
