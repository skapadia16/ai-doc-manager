# =====================================================
# models/user.py — Users, Groups, Members tables
# =====================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

# User ke role (Admin ya Normal User)
class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

# =====================================================
# USERS TABLE
# =====================================================
class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)          # bcrypt hashed
    role          = Column(Enum(UserRole), default=UserRole.user)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships — ek user ke saare documents, conversations etc.
    documents     = relationship("Document", back_populates="uploader")
    conversations = relationship("Conversation", back_populates="user")
    group_members = relationship("GroupMember", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")

# =====================================================
# USER GROUPS TABLE — e.g. "HR Team", "Engineering"
# =====================================================
class UserGroup(Base):
    __tablename__ = "user_groups"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    members     = relationship("GroupMember", back_populates="group")

# =====================================================
# GROUP MEMBERS TABLE — kaun kaun kis group mein hai
# =====================================================
class GroupMember(Base):
    __tablename__ = "group_members"

    id       = Column(Integer, primary_key=True, index=True)
    user_id  = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("user_groups.id"), nullable=False)

    user  = relationship("User", back_populates="group_members")
    group = relationship("UserGroup", back_populates="members")
