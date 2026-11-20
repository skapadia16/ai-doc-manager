# =====================================================
# schemas/auth.py — Login/Register ke liye data shapes
# =====================================================
# Pydantic se API request/response validate karte hain
# Galat data aane par automatically error deta hai

from pydantic import BaseModel, EmailStr
from datetime import datetime

# --- Register karne ke liye ---
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

# --- Login ke liye ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# --- Token response (login hone par milega) ---
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    role: str

# --- User info response ---
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy model se seedha banao
