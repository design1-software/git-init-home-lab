from datetime import datetime, timezone
from uuid import uuid4
import socket
import subprocess

from fastapi import FastAPI, HTTPException, Query

from app.logging_store import load_session, save_session
from app.mentor_engine import analyze_ticket
from app.models import (
    AnalyzeTicketRequest,
    AnalyzeTicketResponse,
    HealthResponse,
    RetrievedContextItem,
    SessionRecord,
)
from app.retrieval import kb_status, search_chunks

app = FastAPI(
    title="ARIA AI Mentor Backend",
    description="Evidence-first AI mentor backend for the ARIA training platform.",
    version="0.4.0",
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
        "version": "0.4.0",
    }


def build_kb_query(request: AnalyzeTicketRequest) -> str:
    parts = [
        request.ticket_id,
        request.ticket_title,
        request.ticket_body,
        request.student_evidence or "",
        request.domain,
        request.difficulty,
    ]
    return " ".join(part for part in parts if part).strip()


def to_context_items(kb_results: list[dict]) -> list[RetrievedContextItem]:
    items: list[RetrievedContextItem] = []

    for result in kb_results:
        items.append(
            RetrievedContextItem(
                score=int(result.get("score", 0)),
                source_path=str(result.get("source_path", "")),
                category=str(result.get("category", "")),
                chunk_index=int(result.get("chunk_index", 0)),
                preview=str(result.get("preview", "")),
            )
        )

    return items


@app.post("/mentor/analyze-ticket", response_model=AnalyzeTicketResponse)
def mentor_analyze_ticket(request: AnalyzeTicketRequest) -> AnalyzeTicketResponse:
    session_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    kb_query = build_kb_query(request)
    kb_results = search_chunks(kb_query, limit=5)

    mentor_response, risk_level, next_action, retrieved_sources = analyze_ticket(
        request=request,
        kb_results=kb_results,
    )

    response = AnalyzeTicketResponse(
        session_id=session_id,
        mentor_response=mentor_response,
        risk_level=risk_level,
        next_action=next_action,
        retrieved_sources=retrieved_sources,
        retrieved_context=to_context_items(kb_results),
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
