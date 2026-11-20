# =====================================================
# routers/admin.py — Admin dashboard & user management
# =====================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User, UserGroup, GroupMember, UserRole
from models.document import Document
from models.conversation import Conversation, ChatMessage, ActivityLog
from schemas.auth import UserResponse
from services.auth_service import require_admin, hash_password
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"])

# GET /admin/stats — Dashboard stats
@router.get("/stats")
def get_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return {
        "total_users": db.query(User).count(),
        "total_documents": db.query(Document).count(),
        "processed_documents": db.query(Document).filter(Document.status == "done").count(),
        "total_conversations": db.query(Conversation).count(),
    }

# GET /admin/users — Saare users
@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(User).all()

# PUT /admin/users/{user_id}/toggle — User activate/deactivate
@router.put("/users/{user_id}/toggle")
def toggle_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    user.is_active = not user.is_active
    db.commit()
    return {"message": f"User {'activated' if user.is_active else 'deactivated'}"}

# POST /admin/users — Admin naya user banaye
class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"

@router.post("/users", response_model=UserResponse)
def create_user(request: CreateUserRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")
    
    user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        role=UserRole.admin if request.role == "admin" else UserRole.user
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ---- Groups ----

class GroupRequest(BaseModel):
    name: str
    description: str = ""

# POST /admin/groups — Naya group banao
@router.post("/groups")
def create_group(request: GroupRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    group = UserGroup(name=request.name, description=request.description)
    db.add(group)
    db.commit()
    db.refresh(group)
    return {"id": group.id, "name": group.name}

# GET /admin/groups — Saare groups
@router.get("/groups")
def list_groups(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    groups = db.query(UserGroup).all()
    return [{"id": g.id, "name": g.name, "description": g.description} for g in groups]

# POST /admin/groups/{group_id}/members — User ko group mein daalo
class AddMemberRequest(BaseModel):
    user_id: int

@router.post("/groups/{group_id}/members")
def add_member(group_id: int, request: AddMemberRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    member = GroupMember(group_id=group_id, user_id=request.user_id)
    db.add(member)
    db.commit()
    return {"message": "Member added"}

# GET /admin/activity — Recent activities
@router.get("/activity")
def get_activity(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    logs = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(50).all()
    return [{"id": l.id, "action": l.action, "details": l.details, "created_at": l.created_at} for l in logs]
