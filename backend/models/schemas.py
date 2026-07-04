"""Data models and schemas"""

from pydantic import BaseModel
from typing import Optional, Any

class HealthResponse(BaseModel):
    status: str
    service: str

class DiagnosisRequest(BaseModel):
    cluster_context: Optional[str] = None
    issue_description: str

class DiagnosisResponse(BaseModel):
    root_cause: str
    explanation: str
    fix: str
    kubectl_command: str
    prevention: str
    confidence: int

class InvestigationResponse(BaseModel):
    status: str
    timestamp: str
    investigation: Optional[dict[str, Any]] = None
    diagnosis: Optional[DiagnosisResponse] = None
    diagnosis_status: Optional[str] = None
    error: Optional[str] = None
