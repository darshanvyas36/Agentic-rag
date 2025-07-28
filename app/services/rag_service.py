import numpy as np
import google.generativeai as genai
from qdrant_client import QdrantClient, models
from app.core.config import settings
from bson import ObjectId
import uuid

# --- Qdrant and Gemini Configuration ---
genai.configure(api_key=settings.GOOGLE_API_KEY)
EMBEDDING_MODEL = "models/embedding-001"
QDRANT_COLLECTION_NAME = "rag_documents"
DIMENSION = 768

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=settings.QDRANT_URL, 
    api_key=settings.QDRANT_API_KEY
)

# Check if the collection exists, and create it if it doesn't
try:
    collection_info = qdrant_client.get_collection(collection_name=QDRANT_COLLECTION_NAME)
    print("✅ Qdrant collection already exists.")
except Exception as e:
    print("Qdrant collection not found. Creating new collection...")
    qdrant_client.create_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=models.VectorParams(size=DIMENSION, distance=models.Distance.COSINE),
    )
    print("✅ New Qdrant collection created.")


def add_chunks_to_rag(chunks: list[str], document_id: str):
    """
    Embeds text chunks and upserts them into the Qdrant collection.
    """
    if not chunks:
        return

    try:
        # Generate embeddings
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=chunks,
            task_type="retrieval_document"
        )
        embeddings = result['embedding']

        # Prepare points for Qdrant
        points = []
        for i, chunk_text in enumerate(chunks):
            points.append(models.PointStruct(
                id=str(uuid.uuid4()),  # Generate a unique ID for each point
                vector=embeddings[i],
                payload={
                    "text": chunk_text,
                    "document_id": document_id
                }
            ))
        
        # Upsert points to Qdrant
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points,
            wait=True
        )
        print(f"✅ Added {len(chunks)} vectors to Qdrant.")

    except Exception as e:
        print(f"❌ Error in add_chunks_to_rag: {e}")
        raise

def search_rag(query: str, top_k: int = 3) -> list[str]:
    """
    Searches the Qdrant collection for relevant text chunks.
    """
    try:
        # Embed the query
        query_embedding = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=query,
            task_type="retrieval_query"
        )['embedding']

        # Search Qdrant for similar vectors
        search_result = qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_embedding,
            limit=top_k
        )
        
        # Return the text from the payload of the results
        return [hit.payload['text'] for hit in search_result]

    except Exception as e:
        print(f"❌ Error in RAG search: {e}")
        return []