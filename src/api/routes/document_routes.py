import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from src.services.rag_service import rag_service

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form("default_user")
):
    """Upload a document and index it in the vector DB for RAG."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
        
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.pdf', '.docx', '.txt', '.md', '.csv']:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
        
    file_path = os.path.join(UPLOAD_DIR, f"{user_id}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result = rag_service.process_document(user_id, file_path, file.filename)
        return {"message": "Document uploaded and indexed successfully", "data": result}
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_documents(user_id: str = "default_user"):
    """Get all documents uploaded by the user."""
    try:
        docs = rag_service.get_user_documents(user_id)
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{doc_id}")
async def delete_document(doc_id: str, user_id: str = "default_user"):
    """Delete a document from the vector DB."""
    try:
        success = rag_service.delete_document(user_id, doc_id)
        if success:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
