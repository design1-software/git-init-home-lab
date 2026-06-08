from datetime import datetime, timezone
from uuid import uuid4
import socket
import subprocess

from fastapi import FastAPI, HTTPException, Query

from app.logging_store import load_session, save_session
from app.mentor_engine import analyze_ticket
from app.models import AnalyzeTicketRequest, AnalyzeTicketResponse, HealthResponse, SessionRecord
from app.retrieval import kb_status, search_chunks

app = FastAPI(
    title="ARIA AI Mentor Backend",
    description="Evidence-first AI mentor backend for the ARIA training platform.",
    version="0.3.0",
)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="aria-ai-mentor",
        hostname=socket.gethostname(),
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        mode="local-dev",
    )


@app.get("/")
def root() -> dict:
    return {
        "service": "ARIA AI Mentor Backend",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "mentor_endpoint": "/mentor/analyze-ticket",
        "kb_status": "/kb/status",
        "kb_search": "/kb/search?q=ticket-009",
    }


@app.post("/mentor/analyze-ticket", response_model=AnalyzeTicketResponse)
def mentor_analyze_ticket(request: AnalyzeTicketRequest) -> AnalyzeTicketResponse:
    session_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    mentor_response, risk_level, next_action, retrieved_sources = analyze_ticket(request)

    response = AnalyzeTicketResponse(
        session_id=session_id,
        mentor_response=mentor_response,
        risk_level=risk_level,
        next_action=next_action,
        retrieved_sources=retrieved_sources,
        timestamp_utc=timestamp,
    )

    save_session(
        SessionRecord(
            session_id=session_id,
            timestamp_utc=timestamp,
            request=request,
            response=response,
        )
    )

    return response


@app.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict:
    record = load_session(session_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return record


@app.get("/kb/status")
def get_kb_status() -> dict:
    return kb_status()


@app.get("/kb/search")
def search_kb(q: str = Query(..., min_length=2), limit: int = Query(default=5, ge=1, le=20)) -> dict:
    return {
        "query": q,
        "limit": limit,
        "results": search_chunks(q, limit=limit),
    }


@app.post("/kb/rebuild")
def rebuild_kb() -> dict:
    result = subprocess.run(
        [
            "/opt/aria-ai-mentor/.venv/bin/python",
            "/opt/aria-ai-mentor/scripts/ingest_docs.py",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "KB rebuild failed",
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
        )

    return {
        "status": "rebuilt",
        "stdout": result.stdout,
    }
