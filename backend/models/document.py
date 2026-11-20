# =====================================================
# models/document.py — Documents & Permissions tables
# =====================================================

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

# Document processing ke stages
class DocStatus(str, enum.Enum):
    pending    = "pending"     # Upload ho gaya, process nahi hua
    processing = "processing"  # RAG pipeline chal rahi hai
    done       = "done"        # Vector DB mein save ho gaya
    failed     = "failed"      # Koi error aaya

# =====================================================
# DOCUMENTS TABLE
# =====================================================
class Document(Base):
    __tablename__ = "documents"

    id            = Column(Integer, primary_key=True, index=True)
    filename      = Column(String, nullable=False)       # Disk par save ka naam
    original_name = Column(String, nullable=False)       # User ne jo naam diya tha
    file_type     = Column(String, nullable=False)       # pdf, docx, txt, csv, xlsx
    file_size     = Column(BigInteger, nullable=False)   # bytes mein
    status        = Column(Enum(DocStatus), default=DocStatus.pending)
    uploaded_by   = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    uploader    = relationship("User", back_populates="documents")
    permissions = relationship("DocumentPermission", back_populates="document")
    chunks      = relationship("DocumentChunk", back_populates="document")

# =====================================================
# DOCUMENT PERMISSIONS TABLE
# Kaun sa user ya group ye document dekh sakta hai
# =====================================================
class DocumentPermission(Base):
    __tablename__ = "document_permissions"

    id          = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=True)   # specific user
    group_id    = Column(Integer, ForeignKey("user_groups.id"), nullable=True)  # ya group

    document = relationship("Document", back_populates="permissions")

# =====================================================
# DOCUMENT CHUNKS TABLE
# RAG ke liye document ke tukde (chunks)
# =====================================================
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id          = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # 0, 1, 2... chunk number
    content        = Column(String, nullable=False)   # actual text
    chunk_metadata = Column(JSON, nullable=True)     # page number etc.

    document = relationship("Document", back_populates="chunks")
