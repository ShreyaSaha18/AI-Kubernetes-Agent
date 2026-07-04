"""Database models for investigations and users"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Investigation(BaseModel):
    """Investigation record"""
    id: Optional[str] = None
    user_id: Optional[str] = None
    root_cause: str
    explanation: str
    fix: str
    kubectl_command: str
    confidence: int
    status: str = "success"
    timestamp: Optional[str] = None
    investigation_data: Optional[dict] = None

class InvestigationHistory(BaseModel):
    """Investigation history entry"""
    id: str
    root_cause: str
    confidence: int
    timestamp: str
    status: str

class User(BaseModel):
    """User model"""
    id: Optional[str] = None
    email: str
    created_at: Optional[str] = None

class AuthRequest(BaseModel):
    """Authentication request"""
    email: str
    password: str

class AuthResponse(BaseModel):
    """Authentication response"""
    user: User
    access_token: str
    session_id: str
