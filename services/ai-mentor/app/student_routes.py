from datetime import datetime, timezone
from html import unescape
import re
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
from app.student_profile import get_student_profile
from app.zammad_client import (
    ZammadClientError,
    get_student_tickets,
    get_ticket,
    get_ticket_articles,
    get_ticket_by_number,
    summarize_ticket_for_mentor,
)

router = APIRouter()


def clean_zammad_text(value: str) -> str:
    text = str(value or "")
    text = re.sub(r"<\s*br\s*/?\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</\s*(div|p|li|tr|h[1-6])\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def lab_ticket_id_from_template(lab_template: dict[str, Any], fallback: str) -> str:
    template_id = str(lab_template.get("template_id") or "")
    match = re.search(r"ticket-(\d{1,3})", template_id)
    if match:
        return match.group(1).zfill(3)
    return str(fallback or "").strip()


def build_student_kb_query(request: AnalyzeTicketRequest) -> str:
    parts = [request.ticket_id, request.ticket_title, request.ticket_body, request.student_evidence or "", request.domain, request.difficulty]
    return " ".join(part for part in parts if part).strip()


def to_student_context_items(kb_results: list[dict]) -> list[RetrievedContextItem]:
    items: list[RetrievedContextItem] = []
    for result in kb_results:
        items.append(RetrievedContextItem(score=int(result.get("score", 0)), source_path=str(result.get("source_path", "")), category=str(result.get("category", "")), chunk_index=int(result.get("chunk_index", 0)), preview=str(result.get("preview", ""))))
    return items


def run_student_analysis(request: AnalyzeTicketRequest) -> AnalyzeTicketResponse:
    session_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    kb_query = build_student_kb_query(request)
    kb_results = search_chunks(kb_query, limit=5)
    mentor_response, risk_level, next_action, retrieved_sources = analyze_ticket(request=request, kb_results=kb_results)
    lab_template = build_lab_template_context(match_lab_template(kb_query))
    if lab_template.get("matched"):
        mentor_response = append_template_guidance(mentor_response, lab_template)
        template_source = f"lab_template:{lab_template.get('template_id')}"
        if template_source not in retrieved_sources:
            retrieved_sources.append(template_source)
    response = AnalyzeTicketResponse(session_id=session_id, mentor_response=mentor_response, risk_level=risk_level, next_action=next_action, retrieved_sources=retrieved_sources, retrieved_context=to_student_context_items(kb_results), timestamp_utc=timestamp, lab_template=lab_template)
    save_session(SessionRecord(session_id=session_id, timestamp_utc=timestamp, request=request, response=response))
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
    safe_sources = [source for source in response.retrieved_sources if source.startswith("labs/") or source.startswith("docs/") or source.startswith("lab_template:")]
    return {"session_id": response.session_id, "mentor_response": response.mentor_response, "risk_level": response.risk_level, "next_action": response.next_action, "retrieved_sources": safe_sources, "timestamp_utc": response.timestamp_utc, "lab_template": safe_template}


def article_text_for_student(articles: list[dict]) -> str:
    safe_parts = []
    for article in articles:
        body = clean_zammad_text(str(article.get("body") or ""))
        subject = clean_zammad_text(str(article.get("subject") or ""))
        if subject or body:
            safe_parts.append("\n".join(part for part in [subject, body] if part))
    return "\n\n".join(safe_parts).strip()


def build_student_workflow(profile: dict[str, Any], lab_template: dict[str, Any]) -> dict[str, Any]:
    return {
        "what_to_open": ["Zammad ticket record", "ARIA AI Mentor student panel", "Assigned lab target system", "Temporary notes area"],
        "target_systems": profile.get("target_systems", []),
        "required_evidence": lab_template.get("required_evidence", []) if lab_template else [],
        "student_steps": ["Read the Zammad ticket.", "Load the ticket in ARIA AI Mentor.", "Review the required evidence list.", "Run commands only on the assigned lab target system.", "Paste real command output or observed results into ARIA.", "Validate the evidence in ARIA.", "Draft the final ticket note and copy it into Zammad after review."],
    }


def build_ticket_context(ticket: dict, articles: list[dict], username: str) -> dict[str, Any]:
    ticket_summary = summarize_ticket_for_mentor(ticket, articles)
    ticket_meta = ticket_summary.get("ticket", {})
    profile = get_student_profile(username)
    title = clean_zammad_text(str(ticket_meta.get("title") or ""))
    body = article_text_for_student(articles) or title
    zammad_number = str(ticket_meta.get("number") or ticket_meta.get("id") or "")
    kb_query = f"{zammad_number} {title} {body}"
    lab_template = build_lab_template_context(match_lab_template(kb_query))
    mentor_ticket_id = lab_ticket_id_from_template(lab_template, zammad_number)
    return {"zammad_ticket": ticket_summary, "student_profile": profile, "mentor_prefill": {"ticket_id": mentor_ticket_id, "zammad_ticket_number": zammad_number, "ticket_title": title, "ticket_body": body, "domain": lab_template.get("domain") or "helpdesk", "difficulty": lab_template.get("difficulty") or "beginner"}, "lab_template": lab_template, "workflow": build_student_workflow(profile, lab_template)}


def build_evidence_guidance(lab_template: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    template_id = str(lab_template.get("template_id") or "").lower()
    domain = str(lab_template.get("domain") or "helpdesk").lower()
    required_evidence = lab_template.get("required_evidence", []) or []
    windows_commands: list[str] = []
    linux_commands: list[str] = []
    if "ticket-001" in template_id or "dns" in domain:
        windows_commands = ["ipconfig /all", "ping 8.8.8.8", "nslookup google.com", "nslookup jlm.lab"]
        linux_commands = ["ip addr", "ip route", "cat /etc/resolv.conf", "ping -c 4 8.8.8.8", "nslookup google.com"]
    elif "linux" in domain or "proxmox" in domain:
        linux_commands = ["whoami", "hostname", "ip -br addr", "ip route", "systemctl --failed"]
    else:
        linux_commands = ["whoami", "hostname", "date", "ip -br addr"]
    return {"message": "Collect real command output or observed results before validating evidence.", "required_evidence": required_evidence, "windows_commands": windows_commands, "linux_commands": linux_commands, "target_systems": profile.get("target_systems", []), "safety_rule": "Do not paste secrets or unrelated personal information."}


def build_final_note(payload: dict[str, Any], username: str) -> str:
    ticket_title = str(payload.get("ticket_title") or "Ticket").strip()
    evidence = str(payload.get("student_evidence") or "").strip()
    next_action = str(payload.get("next_action") or "").strip()
    if not evidence:
        raise ValueError("student_evidence is required before drafting a final note.")
    return f"""Summary:
Worked on {ticket_title}. The reported issue was reviewed through the ARIA evidence-first workflow.

Evidence Collected:
{evidence}

Root Cause or Finding:
Based on the submitted evidence, document the most likely cause here. Do not claim a root cause that was not proven by command output or observed system state.

Action Taken or Recommended:
Document the action taken, the recommended next step, or the reason escalation is needed.

Verification:
Document the verification test that proves the service or issue state after troubleshooting.

Escalation Needed:
Yes/No - explain why.

ARIA Mentor Status:
{next_action or 'not provided'}

Student:
{username}

Instructor Review Note:
This is a student draft. Instructor should review before the ticket is closed.
""".strip()


@router.get("/student", response_class=HTMLResponse)
def student_panel(request: Request) -> HTMLResponse:
    user = get_optional_user(request)
    if not user:
        write_audit_event(event_type="panel.student_redirect_login", request=request, actor=None, outcome="redirect", target_type="panel", target_id="student")
        return RedirectResponse(url="/login", status_code=303)
    if user.get("role") not in {"admin", "instructor", "student"}:
        write_audit_event(event_type="panel.student_access_denied", request=request, actor=user, outcome="forbidden", target_type="panel", target_id="student", metadata={"role": user.get("role")})
        raise HTTPException(status_code=403, detail="Student, instructor, or admin role required.")
    write_audit_event(event_type="panel.student_access", request=request, actor=user, outcome="success", target_type="panel", target_id="student", metadata={"role": user.get("role")})
    html_path = "/opt/aria-ai-mentor/app/static/student.html"
    with open(html_path, "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())


@router.get("/student/profile")
def get_current_student_profile(user: dict = Depends(require_roles("admin", "instructor", "student"))) -> dict:
    return {"profile": get_student_profile(str(user.get("username") or ""))}


@router.get("/student/zammad/tickets")
def get_my_zammad_tickets(request: Request, limit: int = 25, user: dict = Depends(require_roles("admin", "instructor", "student"))) -> dict:
    profile = get_student_profile(str(user.get("username") or ""))
    try:
        tickets = get_student_tickets(str(profile.get("zammad_login") or ""), limit=limit)
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    write_audit_event(event_type="student.zammad_tickets_viewed", request=request, actor=user, outcome="success", target_type="zammad_ticket_list", target_id=str(profile.get("zammad_login") or ""), metadata={"count": len(tickets)})
    return {"student": user.get("username"), "zammad_login": profile.get("zammad_login"), "tickets": tickets, "count": len(tickets)}


@router.get("/student/zammad/tickets/{ticket_id}/context")
def get_zammad_ticket_context_by_id(ticket_id: int, request: Request, user: dict = Depends(require_roles("admin", "instructor", "student"))) -> dict:
    try:
        ticket = get_ticket(ticket_id)
        articles = get_ticket_articles(ticket_id)
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    context = build_ticket_context(ticket, articles, str(user.get("username") or ""))
    write_audit_event(event_type="student.zammad_ticket_loaded", request=request, actor=user, outcome="success", target_type="zammad_ticket", target_id=str(ticket_id), metadata={"ticket_number": context.get("zammad_ticket", {}).get("ticket", {}).get("number"), "lab_template_id": context.get("lab_template", {}).get("template_id")})
    return context


@router.get("/student/zammad/tickets/by-number/{ticket_number}/context")
def get_zammad_ticket_context_by_number(ticket_number: str, request: Request, user: dict = Depends(require_roles("admin", "instructor", "student"))) -> dict:
    try:
        ticket = get_ticket_by_number(ticket_number)
        articles = get_ticket_articles(int(ticket.get("id")))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Zammad ticket id is invalid.") from exc
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    context = build_ticket_context(ticket, articles, str(user.get("username") or ""))
    write_audit_event(event_type="student.zammad_ticket_number_loaded", request=request, actor=user, outcome="success", target_type="zammad_ticket_number", target_id=str(ticket_number), metadata={"lab_template_id": context.get("lab_template", {}).get("template_id")})
    return context


@router.post("/mentor/student/evidence-guidance")
def mentor_student_evidence_guidance(payload: dict, user: dict = Depends(require_roles("admin", "instructor", "student"))) -> dict:
    ticket_id = str(payload.get("ticket_id") or "").strip()
    title = clean_zammad_text(str(payload.get("ticket_title") or ""))
    body = clean_zammad_text(str(payload.get("ticket_body") or ""))
    kb_query = f"{ticket_id} {title} {body}".strip()
    lab_template = build_lab_template_context(match_lab_template(kb_query))
    profile = get_student_profile(str(user.get("username") or ""))
    return {"lab_template": lab_template, "guidance": build_evidence_guidance(lab_template, profile)}


@router.post("/mentor/student/draft-final-note")
def mentor_student_draft_final_note(payload: dict, request: Request, user: dict = Depends(require_roles("admin", "instructor", "student"))) -> dict:
    try:
        draft = build_final_note(payload, str(user.get("username") or "unknown"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    write_audit_event(event_type="student.final_note_drafted", request=request, actor=user, outcome="success", target_type="mentor_final_note", target_id=str(payload.get("ticket_id") or "unknown"), metadata={"draft_length": len(draft)})
    return {"draft_note": draft, "message": "Copy this draft into Zammad after student and instructor review. This endpoint does not write to Zammad."}


@router.post("/mentor/student/analyze-ticket")
def mentor_student_analyze_ticket(payload: AnalyzeTicketRequest, request: Request, user: dict = Depends(require_roles("admin", "instructor", "student"))) -> dict:
    student_request = payload.model_copy(update={"student": str(user.get("username") or payload.student)})
    response = run_student_analysis(student_request)
    write_audit_event(event_type="mentor.student_guidance_requested", request=request, actor=user, outcome="success", target_type="student_mentor_session", target_id=response.session_id, metadata={"ticket_id": student_request.ticket_id, "next_action": response.next_action, "risk_level": response.risk_level, "lab_template_id": (response.lab_template or {}).get("template_id"), "lab_template_domain": (response.lab_template or {}).get("domain")})
    return build_student_safe_response(response)
