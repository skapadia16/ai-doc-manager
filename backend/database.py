# =====================================================
# database.py — PostgreSQL se connection
# =====================================================
# SQLAlchemy use karta hai database se baat karne ke liye
# Har API request ke liye ek "session" milta hai

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Database engine banao (connection pool)
engine = create_engine(settings.DATABASE_URL)

# Har request ke liye session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sabhi DB models is Base se inherit karenge
Base = declarative_base()

# =====================================================
# get_db() — FastAPI dependency
# Har route function mein "db" parameter ke zariye milega
# Request khatam hone par automatically close hoga
# =====================================================
def get_db():
    db = SessionLocal()
    try:
        yield db  # request ke dauran db dete hain
    finally:
        db.close()  # request khatam hone par close karo
