# schemas/__init__.py
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from schemas.document import DocumentResponse, AssignPermissionRequest
from schemas.chat import AskRequest, AskResponse, MessageResponse, ConversationResponse
