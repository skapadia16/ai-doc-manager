# =====================================================
# routers/chat.py — AI Chatbot endpoints
# =====================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from models.conversation import Conversation, ChatMessage
from schemas.chat import AskRequest, AskResponse, MessageResponse, ConversationResponse, SourceInfo
from services.auth_service import get_current_user
from services.rag_service import answer_question

router = APIRouter(prefix="/chat", tags=["Chatbot"])

# POST /chat/ask — Sawaal poochho
@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    # Conversation: naya ya existing
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id  # sirf apni conversation!
        ).first()
        if not conversation:
            raise HTTPException(404, "Conversation not found")
    else:
        # Naya conversation banao
        conversation = Conversation(
            user_id=current_user.id,
            title=request.question[:50]  # first 50 chars as title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # User ka message save karo
    user_msg = ChatMessage(
        conversation_id=conversation.id,
        role="user",
        content=request.question
    )
    db.add(user_msg)
    db.commit()
    
    # RAG pipeline se jawab lo
    result = answer_question(request.question, current_user, db)
    
    # AI ka jawab save karo
    ai_msg = ChatMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=result["answer"],
        sources=result["sources"]
    )
    db.add(ai_msg)
    db.commit()
    
    return AskResponse(
        conversation_id=conversation.id,
        answer=result["answer"],
        sources=[SourceInfo(**s) for s in result["sources"]]
    )

# GET /chat/conversations — Saari conversations list
@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).all()
    return conversations

# GET /chat/conversations/{id}/messages — Ek conversation ke messages
@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def get_messages(conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Conversation exist karta hai? User ki hai?
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id
    ).order_by(ChatMessage.created_at).all()
    
    return messages

# DELETE /chat/conversations/{id} — Conversation delete karo
@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    
    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted"}
