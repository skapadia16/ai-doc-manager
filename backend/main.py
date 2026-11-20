# =====================================================
# main.py — FastAPI App Entry Point
# =====================================================
# Yahan sab kuch jodta hai:
# - Database tables create
# - Routers register
# - CORS settings (React se connect hone ke liye)
# - Default admin user create

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import engine, Base, SessionLocal
from models import User, UserRole            # sab models import karo (tables banenge)
from models.document import Document, DocumentPermission, DocumentChunk
from models.conversation import Conversation, ChatMessage, ActivityLog
from services.auth_service import hash_password
from routers import auth, documents, chat, admin as admin_router
from config import settings

# =====================================================
# Startup: Database tables + Default admin
# =====================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # App start hone par yeh chale
    print("Starting up...")
    
    # Database mein saari tables banao
    Base.metadata.create_all(bind=engine)
    print("Database tables created!")
    
    # Default admin user banao (pehli baar)
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.role == UserRole.admin).first()
        if not existing_admin:
            admin = User(
                name="Admin",
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                role=UserRole.admin
            )
            db.add(admin)
            db.commit()
            print("Default admin created: admin@example.com / admin123")
    finally:
        db.close()
    
    yield  # App chal raha hai
    
    # App band hone par yeh chale
    print("Shutting down...")

# =====================================================
# FastAPI App
# =====================================================
app = FastAPI(
    title="AI Document Manager",
    description="RAG-based document Q&A system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — React frontend se connect karne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Saare routes register karo
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(admin_router.router)

# Health check
@app.get("/")
def root():
    return {"status": "running", "message": "AI Document Manager API"}
