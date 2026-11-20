# =====================================================
# routers/auth.py — Login & Register endpoints
# =====================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, UserRole
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from services.auth_service import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# POST /auth/register — Naya user banao
@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Check: email pehle se hai?
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")
    
    # Naya user banao
    new_user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),  # never store plain password!
        role=UserRole.user
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# POST /auth/login — Login karke token lo
@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # User dhundo
    user = db.query(User).filter(User.email == request.email).first()
    
    # Password verify karo
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(403, "Account is deactivated")
    
    # JWT token banao
    token = create_access_token(user.id, user.role.value)
    
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        role=user.role.value
    )

# GET /auth/me — Apni info dekho
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
