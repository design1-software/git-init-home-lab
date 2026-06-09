from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnalyzeTicketRequest(BaseModel):
    ticket_id: str = Field(..., examples=["009"])
    student: str = Field(..., examples=["sprather"])
    domain: str = Field(default="helpdesk", examples=["helpdesk"])
    difficulty: str = Field(default="beginner", examples=["beginner"])
    ticket_title: str
    ticket_body: str
    student_evidence: Optional[str] = None


class RetrievedContextItem(BaseModel):
    score: int
    source_path: str
    category: str
    chunk_index: int
    preview: str


class AnalyzeTicketResponse(BaseModel):
    session_id: str
    mentor_response: str
    risk_level: str
    next_action: str
    retrieved_sources: List[str]
    retrieved_context: List[RetrievedContextItem] = []
    timestamp_utc: str
    lab_template: Optional[Dict[str, Any]] = None
    lab_template: Optional[Dict[str, Any]] = None


class SessionRecord(BaseModel):
    session_id: str
    timestamp_utc: str
    request: AnalyzeTicketRequest
    response: AnalyzeTicketResponse


class HealthResponse(BaseModel):
    status: str
    service: str
    hostname: str
    timestamp_utc: str
    mode: str


class ZammadDraftGuidanceResponse(BaseModel):
    ticket_id: int
    session_id: str
    mentor_response: str
    risk_level: str
    next_action: str
    retrieved_sources: List[str]
    retrieved_context: List[RetrievedContextItem] = []
    zammad_ticket: dict
    timestamp_utc: str
    lab_template: Optional[Dict[str, Any]] = None
