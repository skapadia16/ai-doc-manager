# =====================================================
# services/auth_service.py — Password & JWT logic
# =====================================================
# bcrypt se password hash karte hain (safe storage)
# JWT token banate hain (login proof)

import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.user import User

# Bearer token scheme — "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# =====================================================
# Password Functions (Clean & Native bcrypt)
# =====================================================

def hash_password(plain_password: str) -> str:
    """Plain password ko bcrypt hash mein badlo"""
    pwd_bytes = plain_password[:72].encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Login ke waqt password check karo"""
    try:
        pwd_bytes = plain_password[:72].encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False

# =====================================================
# JWT Token Functions
# =====================================================

def create_access_token(user_id: int, role: str) -> str:
    """
    JWT token banao.
    Token ke andar user_id aur role store hota hai.
    Ek expire time bhi hota hai.
    """
    expire_time = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(user_id),   # user ki ID
        "role": role,           # "admin" ya "user"
        "exp": expire_time      # kab expire hoga
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

def decode_token(token: str) -> dict:
    """Token ko decode karke user_id aur role nikalo"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# =====================================================
# FastAPI Dependencies — Routes mein inject honge
# =====================================================

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Har protected route ke liye.
    Token se user nikalo, DB se check karo.
    """
    payload = decode_token(token)
    user_id = int(payload.get("sub"))
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Sirf admin hi access kar sakta hai.
    Normal user ne try kiya to 403 error.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
