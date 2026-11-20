# =====================================================
# services/document_service.py — Document processing
# =====================================================
# Upload → Extract → Chunk → Embed → Store in FAISS

import os
import uuid
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from config import settings
from models.document import Document, DocumentChunk, DocStatus
from models.user import User
from rag.extractor import extract_text
from rag.chunker import split_text_into_chunks
from rag.embedder import embed_texts
from rag.vector_store import get_vector_store

# Allowed file types
ALLOWED_TYPES = {"pdf", "docx", "txt", "csv", "xlsx", "xls"}

def get_file_extension(filename: str) -> str:
    """File ka extension nikalo (lowercase mein)"""
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

def validate_file(file: UploadFile, file_bytes: bytes):
    """File check karo — type aur size"""
    ext = get_file_extension(file.filename)
    
    if ext not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type '{ext}' not allowed. Allowed: {ALLOWED_TYPES}")
    
    if len(file_bytes) > settings.MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large. Max size: {settings.MAX_FILE_SIZE // 1024 // 1024}MB")

def save_file_to_disk(file_bytes: bytes, original_name: str) -> str:
    """File disk par save karo, unique naam se"""
    ext = get_file_extension(original_name)
    unique_name = f"{uuid.uuid4().hex}.{ext}"  # random naam taaki clash na ho
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    
    return unique_name

def process_document(document_id: int, db: Session):
    """
    =====================================================
    RAG Pipeline — Main Function
    =====================================================
    
    Step 1: Document DB se lo
    Step 2: File disk se padho
    Step 3: Text extract karo (PDF/DOCX etc.)
    Step 4: Text ko chunks mein baanto
    Step 5: Chunks embed karo (vectors)
    Step 6: Vectors FAISS mein save karo
    Step 7: Chunks DB mein save karo
    """
    
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return
    
    # Status update: processing shuru
    doc.status = DocStatus.processing
    db.commit()
    
    try:
        # --- Step 2: File padho ---
        file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        
        # --- Step 3: Text extract karo ---
        print(f"Extracting text from {doc.original_name}...")
        text = extract_text(file_bytes, doc.file_type)
        
        if not text.strip():
            raise ValueError("No text could be extracted from document")
        
        # --- Step 4: Chunks banao ---
        print(f"Splitting into chunks...")
        chunks = split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200)
        print(f"Created {len(chunks)} chunks")
        
        # --- Step 5: Embed karo ---
        print(f"Creating embeddings...")
        embeddings = embed_texts(chunks)
        
        # --- Step 6 & 7: FAISS + DB mein save karo ---
        vector_store = get_vector_store(settings.VECTOR_DB_DIR)
        
        # Old chunks delete karo (reprocess case)
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
        
        # Metadata prepare karo
        chunks_info = []
        db_chunks = []
        
        for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            # FAISS ke liye metadata
            chunks_info.append({
                "document_id": document_id,
                "chunk_index": i,
                "text": chunk_text,
                "doc_name": doc.original_name
            })
            
            # DB ke liye chunk record
            db_chunks.append(DocumentChunk(
                document_id=document_id,
                chunk_index=i,
                content=chunk_text,
                chunk_metadata={"doc_name": doc.original_name}
            ))
        
        # FAISS mein add karo
        vector_store.add_chunks(embeddings, chunks_info)
        
        # DB mein save karo
        db.bulk_save_objects(db_chunks)
        
        # Status: done!
        doc.status = DocStatus.done
        db.commit()
        print(f"Document {doc.original_name} processed successfully!")
    
    except Exception as e:
        # Koi error aaya — fail status
        doc.status = DocStatus.failed
        db.commit()
        print(f"Error processing document {doc.original_name}: {e}")
        raise
