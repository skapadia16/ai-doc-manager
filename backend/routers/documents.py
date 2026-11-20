# =====================================================
# routers/documents.py — Document upload & management
# =====================================================

import threading
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from models.document import Document, DocStatus, DocumentPermission
from schemas.document import DocumentResponse, AssignPermissionRequest
from services.auth_service import get_current_user, require_admin
from services.document_service import validate_file, save_file_to_disk, process_document, get_file_extension
from models.conversation import ActivityLog

router = APIRouter(prefix="/documents", tags=["Documents"])

# POST /documents/upload — Document upload karo (Admin only)
@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    # File bytes padho
    file_bytes = file.file.read()
    
    # Validate karo
    validate_file(file, file_bytes)
    
    # Disk par save karo
    saved_name = save_file_to_disk(file_bytes, file.filename)
    
    # DB mein record banao
    doc = Document(
        filename=saved_name,
        original_name=file.filename,
        file_type=get_file_extension(file.filename),
        file_size=len(file_bytes),
        status=DocStatus.pending,
        uploaded_by=admin.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Activity log
    db.add(ActivityLog(user_id=admin.id, action="uploaded_document", details={"doc_id": doc.id, "name": file.filename}))
    db.commit()
    
    # Background mein RAG pipeline chalaao (user ko wait nahi karna)
    background_tasks.add_task(process_document, doc.id, db)
    
    return doc

# GET /documents — Saare documents dekho
@router.get("/", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Admin ko sab, user ko sirf apne
    if current_user.role == "admin":
        docs = db.query(Document).order_by(Document.created_at.desc()).all()
    else:
        # User ke allowed documents
        allowed_ids = [
            p.document_id for p in 
            db.query(DocumentPermission).filter(DocumentPermission.user_id == current_user.id).all()
        ]
        docs = db.query(Document).filter(Document.id.in_(allowed_ids)).all()
    
    return docs

# DELETE /documents/{doc_id} — Document delete karo (Admin only)
@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}

# POST /documents/{doc_id}/reprocess — Dobara process karo
@router.post("/{doc_id}/reprocess")
def reprocess_document(
    doc_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    
    doc.status = DocStatus.pending
    db.commit()
    
    background_tasks.add_task(process_document, doc_id, db)
    return {"message": "Reprocessing started"}

# POST /documents/permissions — User/Group ko access do (Admin only)
@router.post("/permissions")
def assign_permission(request: AssignPermissionRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if not request.user_id and not request.group_id:
        raise HTTPException(400, "Provide user_id or group_id")
    
    # Check if duplicate
    existing = db.query(DocumentPermission).filter(
        DocumentPermission.document_id == request.document_id,
        DocumentPermission.user_id == request.user_id,
        DocumentPermission.group_id == request.group_id
    ).first()
    if existing:
        return {"message": "Permission already exists"}

    perm = DocumentPermission(
        document_id=request.document_id,
        user_id=request.user_id,
        group_id=request.group_id
    )
    db.add(perm)
    db.commit()
    return {"message": "Permission assigned"}

# GET /documents/{doc_id}/permissions — Check kis user ko access hai
@router.get("/{doc_id}/permissions")
def get_document_permissions(doc_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    perms = db.query(DocumentPermission).filter(DocumentPermission.document_id == doc_id).all()
    result = []
    for p in perms:
        user_name = None
        user_email = None
        if p.user_id:
            u = db.query(User).filter(User.id == p.user_id).first()
            if u:
                user_name = u.name
                user_email = u.email
        result.append({
            "id": p.id,
            "document_id": p.document_id,
            "user_id": p.user_id,
            "user_name": user_name,
            "user_email": user_email,
            "group_id": p.group_id
        })
    return result

# DELETE /documents/permissions/{perm_id} — Revoke access
@router.delete("/permissions/{perm_id}")
def revoke_permission(perm_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    perm = db.query(DocumentPermission).filter(DocumentPermission.id == perm_id).first()
    if not perm:
        raise HTTPException(404, "Permission not found")
    db.delete(perm)
    db.commit()
    return {"message": "Permission revoked"}
