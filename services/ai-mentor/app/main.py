from datetime import datetime, timezone
from uuid import uuid4
import socket
import subprocess

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from app.logging_store import load_session, save_session
from app.mentor_engine import analyze_ticket
from app.models import (
    AnalyzeTicketRequest,
    AnalyzeTicketResponse,
    HealthResponse,
    RetrievedContextItem,
    SessionRecord,
    ZammadDraftGuidanceResponse,
)
from app.retrieval import kb_status, search_chunks
from app.zammad_client import (
    ZammadClientError,
    get_ticket,
    get_ticket_articles,
    get_ticket_by_number,
    get_zammad_health,
    summarize_ticket_for_mentor,
)

app = FastAPI(
    title="ARIA AI Mentor Backend",
    description="Evidence-first AI mentor backend for the ARIA training platform.",
    version="0.6.1",
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
        "instructor_panel": "/instructor",
        "mentor_endpoint": "/mentor/analyze-ticket",
        "zammad_health": "/zammad/health",
        "zammad_ticket": "/zammad/tickets/{ticket_id}",
        "zammad_ticket_by_number": "/zammad/tickets/by-number/{ticket_number}",
        "zammad_articles": "/zammad/tickets/{ticket_id}/articles",
        "zammad_draft_guidance": "/mentor/zammad/ticket/{ticket_id}/draft-guidance",
        "zammad_draft_guidance_by_number": "/mentor/zammad/ticket-number/{ticket_number}/draft-guidance",
        "kb_status": "/kb/status",
        "kb_search": "/kb/search?q=ticket-009",
        "version": "0.6.1",
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


def build_zammad_draft_guidance_response(ticket: dict, articles: list[dict]) -> ZammadDraftGuidanceResponse:
    ticket_context = summarize_ticket_for_mentor(ticket, articles)

    internal_ticket_id = int(ticket_context["ticket"].get("id"))
    ticket_title = str(ticket_context["ticket"].get("title") or f"Zammad Ticket {internal_ticket_id}")

    article_text = "\n\n".join(
        str(article.get("body") or "")
        for article in ticket_context["articles"]
        if article.get("body")
    )

    request = AnalyzeTicketRequest(
        ticket_id=str(internal_ticket_id),
        student=str(ticket_context["ticket"].get("customer") or "unknown"),
        domain="helpdesk",
        difficulty="beginner",
        ticket_title=ticket_title,
        ticket_body=article_text or ticket_title,
        student_evidence=article_text,
    )

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

    return ZammadDraftGuidanceResponse(
        ticket_id=internal_ticket_id,
        session_id=session_id,
        mentor_response=mentor_response,
        risk_level=risk_level,
        next_action=next_action,
        retrieved_sources=retrieved_sources,
        retrieved_context=to_context_items(kb_results),
        zammad_ticket=ticket_context,
        timestamp_utc=timestamp,
    )


@app.get("/instructor", response_class=HTMLResponse)
def instructor_panel() -> HTMLResponse:
    html_path = "/opt/aria-ai-mentor/app/static/instructor.html"
    with open(html_path, "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())


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


@app.get("/zammad/health")
def zammad_health() -> dict:
    try:
        return get_zammad_health()
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/zammad/tickets/by-number/{ticket_number}")
def zammad_ticket_by_number(ticket_number: str) -> dict:
    try:
        return get_ticket_by_number(ticket_number)
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/zammad/tickets/{ticket_id}")
def zammad_ticket(ticket_id: int) -> dict:
    try:
        return get_ticket(ticket_id)
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/zammad/tickets/{ticket_id}/articles")
def zammad_ticket_articles(ticket_id: int) -> dict:
    try:
        return {
            "ticket_id": ticket_id,
            "articles": get_ticket_articles(ticket_id),
        }
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/mentor/zammad/ticket/{ticket_id}/draft-guidance", response_model=ZammadDraftGuidanceResponse)
def mentor_zammad_ticket_draft_guidance(ticket_id: int) -> ZammadDraftGuidanceResponse:
    try:
        ticket = get_ticket(ticket_id)
        articles = get_ticket_articles(ticket_id)
        return build_zammad_draft_guidance_response(ticket, articles)
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/mentor/zammad/ticket-number/{ticket_number}/draft-guidance", response_model=ZammadDraftGuidanceResponse)
def mentor_zammad_ticket_number_draft_guidance(ticket_number: str) -> ZammadDraftGuidanceResponse:
    try:
        ticket = get_ticket_by_number(ticket_number)
        ticket_id = int(ticket.get("id"))
        articles = get_ticket_articles(ticket_id)
        return build_zammad_draft_guidance_response(ticket, articles)
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
