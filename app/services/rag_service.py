import faiss
import numpy as np
import google.generativeai as genai
from app.core.config import settings
from app.db.database import chunks_collection
from bson import ObjectId
import os

# --- FAISS and Gemini Configuration ---
genai.configure(api_key=settings.GOOGLE_API_KEY)
EMBEDDING_MODEL = "models/embedding-001"
FAISS_INDEX_PATH = "data/faiss_index.bin"
DIMENSION = 768

def load_or_create_faiss_index(dimension: int) -> faiss.IndexIDMap:
    """Loads a FAISS index from disk or creates a new one if it doesn't exist."""
    os.makedirs("data", exist_ok=True)
    if os.path.exists(FAISS_INDEX_PATH):
        try:
            print("Loading existing FAISS index...")
            return faiss.read_index(FAISS_INDEX_PATH)
        except Exception as e:
            print(f"Error loading FAISS index: {e}. Creating a new one.")
    
    print("Creating new FAISS index...")
    index = faiss.IndexFlatL2(dimension)
    return faiss.IndexIDMap(index)

faiss_index = load_or_create_faiss_index(DIMENSION)

def save_faiss_index():
    """Saves the current FAISS index to disk."""
    try:
        faiss.write_index(faiss_index, FAISS_INDEX_PATH)
        print("✅ FAISS index saved successfully.")
    except Exception as e:
        print(f"❌ Error saving FAISS index: {e}")


def add_chunks_to_rag(chunks: list[str], document_id: str):
    """
    Embeds text chunks, adds them to MongoDB and the FAISS index.
    """
    if not chunks:
        return

    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=chunks,
            task_type="retrieval_document"
        )
        embeddings = result['embedding']

        start_index = faiss_index.ntotal
        faiss_ids = list(range(start_index, start_index + len(chunks)))

        mongo_chunks = []
        for i, chunk_text in enumerate(chunks):
            mongo_chunks.append({
                "_id": ObjectId(),
                "document_id": document_id,
                "text": chunk_text,
                "faiss_id": faiss_ids[i]
            })

        faiss_index.add_with_ids(np.array(embeddings), np.array(faiss_ids))
        save_faiss_index()

        if mongo_chunks:
            chunks_collection.insert_many(mongo_chunks)
            print(f"✅ Added {len(mongo_chunks)} chunks to MongoDB.")

    except Exception as e:
        print(f"❌ Error in add_chunks_to_rag: {e}")
        raise

def search_rag(query: str, top_k: int = 3) -> list[str]:
    """
    Searches the RAG system for relevant text chunks based on a query.
    """
    try:
        query_embedding = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=query,
            task_type="retrieval_query"
        )['embedding']

        distances, ids = faiss_index.search(np.array([query_embedding]), top_k)
        retrieved_ids = [int(i) for i in ids[0] if i != -1]
        
        if not retrieved_ids:
            return []

        retrieved_docs = chunks_collection.find({"faiss_id": {"$in": retrieved_ids}})
        return [doc['text'] for doc in retrieved_docs]

    except Exception as e:
        print(f"❌ Error in RAG search: {e}")
        return []
    