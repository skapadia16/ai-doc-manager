# =====================================================
# schemas/chat.py — Chat API ke liye shapes
# =====================================================

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# --- Sawaal poochne ke liye ---
class AskRequest(BaseModel):
    conversation_id: Optional[int] = None  # existing conversation ya naya
    question: str

# --- Source reference (document ka naam aur chunk) ---
class SourceInfo(BaseModel):
    document_name: str
    chunk_index: int

# --- AI ka jawab ---
class AskResponse(BaseModel):
    conversation_id: int
    answer: str
    sources: List[SourceInfo]  # kahan se mila jawab

# --- Ek message ---
class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[List] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Conversation list ke liye ---
class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True
