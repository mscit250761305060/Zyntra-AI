import os
import uuid
import logging
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import pdfplumber
import docx
import markdown
import csv

logger = logging.getLogger("zyntra.rag_service")

# Data directory for chromadb
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "chroma")
os.makedirs(DATA_DIR, exist_ok=True)

class RAGService:
    def __init__(self):
        self.last_search_results = {}
        # Attempt to initialize ChromaDB; if the persistent store is corrupted or incompatible, clean it up and retry.
        for attempt in range(2):
            try:
                self.client = chromadb.PersistentClient(path=DATA_DIR, settings=Settings(allow_reset=True))
                # Create or get collection
                self.collection = self.client.get_or_create_collection(
                    name="user_documents",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("ChromaDB initialized successfully.")
                break  # Success, exit retry loop
            except BaseException as e:
                logger.error(f"Failed to initialize ChromaDB (attempt {attempt + 1}): {e}")
                # If first attempt fails, try to remove the corrupted data directory and retry
                if attempt == 0:
                    try:
                        import shutil
                        if os.path.isdir(DATA_DIR):
                            shutil.rmtree(DATA_DIR)
                            logger.info(f"Removed corrupted ChromaDB data directory {DATA_DIR}, retrying initialization.")
                        os.makedirs(DATA_DIR, exist_ok=True)
                    except BaseException as cleanup_err:
                        logger.error(f"Failed to clean up ChromaDB data directory: {cleanup_err}")
                else:
                    # Second attempt also failed; give up and set client/collection to None
                    self.client = None
                    self.collection = None

    def _extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from various file formats."""
        ext = os.path.splitext(filename)[1].lower()
        text = ""
        
        try:
            if ext == '.pdf':
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
            elif ext == '.docx':
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            elif ext == '.csv':
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        text += " ".join(row) + "\n"
            elif ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {e}")
            raise e

        return text

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Simple character-based chunking with overlap."""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunks.append(text[start:end])
            start += chunk_size - overlap
            
        return chunks

    def process_document(self, user_id: str, file_path: str, filename: str) -> Dict[str, Any]:
        """Extract text, chunk, and store in ChromaDB."""
        if not self.collection:
            raise RuntimeError("ChromaDB collection not initialized")

        # 1. Extract text
        text = self._extract_text(file_path, filename)
        if not text.strip():
            raise ValueError(f"No text extracted from {filename}")

        # 2. Chunk text
        chunks = self._chunk_text(text)
        
        # 3. Store in Vector DB
        doc_id = str(uuid.uuid4())
        
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{i}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "user_id": user_id,
                "doc_id": doc_id,
                "filename": filename,
                "chunk_index": i
            })

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return {
            "doc_id": doc_id,
            "filename": filename,
            "chunks_count": len(chunks)
        }

    def search(self, user_id: str, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant chunks for a specific user."""
        if not self.collection:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"user_id": user_id}
        )
        
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results and results['distances'] else 0
                })
                
        self.last_search_results[user_id] = formatted_results
        return formatted_results

    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """List all unique documents uploaded by the user."""
        if not self.collection:
            return []
            
        results = self.collection.get(
            where={"user_id": user_id},
            include=["metadatas"]
        )
        
        # Extract unique documents
        docs = {}
        for meta in results['metadatas']:
            doc_id = meta['doc_id']
            if doc_id not in docs:
                docs[doc_id] = {
                    "doc_id": doc_id,
                    "filename": meta['filename']
                }
                
        return list(docs.values())

    def delete_document(self, user_id: str, doc_id: str) -> bool:
        """Delete a specific document and all its chunks."""
        if not self.collection:
            return False
            
        self.collection.delete(
            where={
                "$and": [
                    {"user_id": user_id},
                    {"doc_id": doc_id}
                ]
            }
        )
        return True

rag_service = RAGService()
