from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.audit import write_audit_event
from app.auth import get_optional_user, require_roles
from app.lab_templates import (
    append_template_guidance,
    build_lab_template_context,
    match_lab_template,
)
from app.logging_store import save_session
from app.mentor_engine import analyze_ticket
from app.models import (
    AnalyzeTicketRequest,
    AnalyzeTicketResponse,
    RetrievedContextItem,
    SessionRecord,
)
from app.retrieval import search_chunks

router = APIRouter()


def build_student_kb_query(request: AnalyzeTicketRequest) -> str:
    parts = [
        request.ticket_id,
        request.ticket_title,
        request.ticket_body,
        request.student_evidence or "",
        request.domain,
        request.difficulty,
    ]
    return " ".join(part for part in parts if part).strip()


def to_student_context_items(kb_results: list[dict]) -> list[RetrievedContextItem]:
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


def run_student_analysis(request: AnalyzeTicketRequest) -> AnalyzeTicketResponse:
    session_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    kb_query = build_student_kb_query(request)
    kb_results = search_chunks(kb_query, limit=5)

    mentor_response, risk_level, next_action, retrieved_sources = analyze_ticket(
        request=request,
        kb_results=kb_results,
    )

    lab_template = build_lab_template_context(match_lab_template(kb_query))
    if lab_template.get("matched"):
        mentor_response = append_template_guidance(mentor_response, lab_template)
        template_source = f"lab_template:{lab_template.get('template_id')}"
        if template_source not in retrieved_sources:
            retrieved_sources.append(template_source)

    response = AnalyzeTicketResponse(
        session_id=session_id,
        mentor_response=mentor_response,
        risk_level=risk_level,
        next_action=next_action,
        retrieved_sources=retrieved_sources,
        retrieved_context=to_student_context_items(kb_results),
        timestamp_utc=timestamp,
        lab_template=lab_template,
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


def build_student_safe_response(response: AnalyzeTicketResponse) -> dict[str, Any]:
    lab_template = response.lab_template or {}

    safe_template = {
        "matched": bool(lab_template.get("matched", False)),
        "template_id": lab_template.get("template_id"),
        "title": lab_template.get("title"),
        "domain": lab_template.get("domain"),
        "difficulty": lab_template.get("difficulty"),
        "mentor_mode": lab_template.get("mentor_mode"),
        "required_evidence": lab_template.get("required_evidence", []),
        "opening_questions": lab_template.get("opening_questions", []),
        "completion_signals": lab_template.get("completion_signals", []),
    }

    safe_sources = [
        source
        for source in response.retrieved_sources
        if source.startswith("labs/")
        or source.startswith("docs/")
        or source.startswith("lab_template:")
    ]

    return {
        "session_id": response.session_id,
        "mentor_response": response.mentor_response,
        "risk_level": response.risk_level,
        "next_action": response.next_action,
        "retrieved_sources": safe_sources,
        "timestamp_utc": response.timestamp_utc,
        "lab_template": safe_template,
    }


@router.get("/student", response_class=HTMLResponse)
def student_panel(request: Request) -> HTMLResponse:
    user = get_optional_user(request)

    if not user:
        write_audit_event(
            event_type="panel.student_redirect_login",
            request=request,
            actor=None,
            outcome="redirect",
            target_type="panel",
            target_id="student",
        )
        return RedirectResponse(url="/login", status_code=303)

    if user.get("role") not in {"admin", "instructor", "student"}:
        write_audit_event(
            event_type="panel.student_access_denied",
            request=request,
            actor=user,
            outcome="forbidden",
            target_type="panel",
            target_id="student",
            metadata={"role": user.get("role")},
        )
        raise HTTPException(
            status_code=403,
            detail="Student, instructor, or admin role required.",
        )

    write_audit_event(
        event_type="panel.student_access",
        request=request,
        actor=user,
        outcome="success",
        target_type="panel",
        target_id="student",
        metadata={"role": user.get("role")},
    )

    html_path = "/opt/aria-ai-mentor/app/static/student.html"
    with open(html_path, "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())


@router.post("/mentor/student/analyze-ticket")
def mentor_student_analyze_ticket(
    payload: AnalyzeTicketRequest,
    request: Request,
    user: dict = Depends(require_roles("admin", "instructor", "student")),
) -> dict:
    student_request = payload.model_copy(
        update={"student": str(user.get("username") or payload.student)}
    )

    response = run_student_analysis(student_request)

    write_audit_event(
        event_type="mentor.student_guidance_requested",
        request=request,
        actor=user,
        outcome="success",
        target_type="student_mentor_session",
        target_id=response.session_id,
        metadata={
            "ticket_id": student_request.ticket_id,
            "next_action": response.next_action,
            "risk_level": response.risk_level,
            "lab_template_id": (response.lab_template or {}).get("template_id"),
            "lab_template_domain": (response.lab_template or {}).get("domain"),
        },
    )

    return build_student_safe_response(response)
