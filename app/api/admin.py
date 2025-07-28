from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from typing import List
from datetime import datetime
from bson import ObjectId
import numpy as np

# Import services
from app.services import document_service, rag_service
from app.services.rag_service import faiss_index, save_faiss_index

# Import database collections and the db dependency
from app.db.database import documents_collection, chunks_collection, get_db

# Import Pydantic schemas
from app.schemas.schemas import Document, DocumentUploadResponse

# This line is correct
router = APIRouter()

# --- CHANGE THIS ENDPOINT ---
# The path needs to include "/admin"
@router.post("/admin/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), db=Depends(get_db)):
    """
    Endpoint to upload a document, process it, and add it to the RAG system.
    """
    # ... (function body remains the same) ...
    try:
        text_chunks = await document_service.process_document_file(file)
        document_metadata = {
            "filename": file.filename,
            "upload_date": datetime.utcnow(),
            "file_size": file.size,
        }
        insert_result = documents_collection.insert_one(document_metadata)
        document_id = str(insert_result.inserted_id)
        rag_service.add_chunks_to_rag(chunks=text_chunks, document_id=document_id)
        return DocumentUploadResponse(
            message="Document uploaded and processed successfully.",
            document_id=document_id,
            filename=file.filename
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )


# --- CHANGE THIS ENDPOINT ---
# The path needs to include "/admin"
@router.get("/admin/documents", response_model=List[Document])
async def list_documents(db=Depends(get_db)):
    """
    Endpoint to list all documents from the database.
    """
    # ... (function body remains the same) ...
    try:
        all_docs = list(documents_collection.find({}))
        for doc in all_docs:
            doc["_id"] = str(doc["_id"])
        return all_docs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch documents: {e}"
        )
    
# Add this new function
@router.delete("/admin/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: str, db=Depends(get_db)):
    """
    Deletes a document, its chunks from MongoDB, and its vectors from FAISS.
    """
    try:
        # 1. Find all chunks related to the document to get their FAISS IDs
        chunks_to_delete = list(chunks_collection.find({"document_id": doc_id}))
        if chunks_to_delete:
            faiss_ids_to_remove = [chunk['faiss_id'] for chunk in chunks_to_delete]
            
            # 2. Remove vectors from FAISS index
            # Note: FAISS requires the IDs to be of type int64
            faiss_index.remove_ids(np.array(faiss_ids_to_remove, dtype=np.int64))
            save_faiss_index() # Save the changes to the index file
            print(f"✅ Removed {len(faiss_ids_to_remove)} vectors from FAISS.")

            # 3. Delete the chunks from MongoDB
            chunks_collection.delete_many({"document_id": doc_id})

        # 4. Delete the document metadata itself
        delete_result = documents_collection.delete_one({"_id": ObjectId(doc_id)})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Document not found.")

        return

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the document: {e}"
        )