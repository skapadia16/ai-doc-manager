# =====================================================
# schemas/document.py — Document API ke liye shapes
# =====================================================

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# --- Document response (list/detail mein aayega) ---
class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_name: str
    file_type: str
    file_size: int
    status: str
    uploaded_by: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Permission assign karne ke liye ---
class AssignPermissionRequest(BaseModel):
    document_id: int
    user_id: Optional[int] = None    # specific user ko dena
    group_id: Optional[int] = None   # ya poore group ko dena
