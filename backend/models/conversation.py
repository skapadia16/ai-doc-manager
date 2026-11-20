# =====================================================
# models/conversation.py — Chat History tables
# =====================================================

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# =====================================================
# CONVERSATIONS TABLE
# Ek user ke multiple conversations ho sakte hain
# (jaise ChatGPT mein left sidebar mein)
# =====================================================
class Conversation(Base):
    __tablename__ = "conversations"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    title      = Column(String, default="New Conversation")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user     = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation")

# =====================================================
# CHAT MESSAGES TABLE
# Har conversation ke andar user + AI messages
# =====================================================
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id              = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role            = Column(String, nullable=False)   # "user" ya "assistant"
    content         = Column(Text, nullable=False)     # message text
    sources         = Column(JSON, nullable=True)      # [{doc_name, chunk_index}]
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")

# =====================================================
# ACTIVITY LOGS TABLE
# Admin ke liye — kaun ne kya kiya
# =====================================================
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=True)
    action     = Column(String, nullable=False)   # e.g. "uploaded_document"
    details    = Column(JSON, nullable=True)      # extra info
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="activity_logs")
