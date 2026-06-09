from datetime import datetime, timezone
from uuid import uuid4
import socket
import subprocess

from fastapi import FastAPI, HTTPException, Query, Request, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from app.audit import (
    audit_status,
    read_recent_audit_events,
    write_audit_event,
)
from app.auth import (
    COOKIE_NAME,
    LoginRequest,
    auth_status,
    authenticate_user,
    create_session_token,
    get_current_user,
    get_optional_user,
    require_roles,
    session_ttl_seconds,
)
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
from app.llm_client import LLMClientError, enhance_guidance, llm_status
from app.lab_templates import (
    append_template_guidance,
    build_lab_template_context,
    get_lab_template,
    lab_template_status,
    list_lab_template_summaries,
    match_lab_template,
)
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
    version="0.6.0",
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
        "zammad_health": "/zammad/health",
        "zammad_ticket": "/zammad/tickets/{ticket_id}",
        "zammad_ticket_by_number": "/zammad/tickets/by-number/{ticket_number}",
        "zammad_articles": "/zammad/tickets/{ticket_id}/articles",
        "zammad_draft_guidance": "/mentor/zammad/ticket/{ticket_id}/draft-guidance",
        "zammad_draft_guidance_by_number": "/mentor/zammad/ticket-number/{ticket_number}/draft-guidance",
        "kb_status": "/kb/status",
        "kb_search": "/kb/search?q=ticket-009",
        "version": "0.6.0",
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
        retrieved_context=to_context_items(kb_results),
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
        lab_template=lab_template,
    )


@app.get("/login", response_class=HTMLResponse)
def login_page() -> HTMLResponse:
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ARIA Mentor Login</title>
  <style>
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      font-family: Arial, Helvetica, sans-serif;
      background: #0f172a;
      color: #e5e7eb;
    }
    .card {
      width: min(420px, 92vw);
      background: #111827;
      border: 1px solid #374151;
      border-radius: 14px;
      padding: 26px;
    }
    h1 { margin: 0 0 8px; }
    p { color: #9ca3af; }
    label {
      display: block;
      margin-top: 14px;
      margin-bottom: 6px;
      font-weight: bold;
    }
    input {
      width: 100%;
      padding: 12px;
      border-radius: 8px;
      border: 1px solid #374151;
      background: #020617;
      color: #e5e7eb;
      font-size: 16px;
    }
    button {
      width: 100%;
      margin-top: 18px;
      padding: 12px;
      border: 0;
      border-radius: 8px;
      background: #38bdf8;
      color: #020617;
      font-weight: bold;
      font-size: 16px;
      cursor: pointer;
    }
    .error {
      margin-top: 14px;
      color: #fecaca;
      background: rgba(239, 68, 68, 0.12);
      border: 1px solid rgba(239, 68, 68, 0.45);
      padding: 10px;
      border-radius: 8px;
      display: none;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>ARIA Mentor Login</h1>
    <p>Sign in to access the instructor panel.</p>

    <label for="username">Username</label>
    <input id="username" autocomplete="username" />

    <label for="password">Password</label>
    <input id="password" type="password" autocomplete="current-password" />

    <button onclick="login()">Sign In</button>
    <div id="error" class="error"></div>
  </div>

  <script>
    async function login() {
      const errorBox = document.getElementById('error');
      errorBox.style.display = 'none';
      errorBox.textContent = '';

      const username = document.getElementById('username').value.trim();
      const password = document.getElementById('password').value;

      try {
        const response = await fetch('/auth/login', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({username, password})
        });

        if (!response.ok) {
          throw new Error('Invalid username or password.');
        }

        const data = await response.json();
        window.location.href = data.redirect || '/instructor';
      } catch (error) {
        errorBox.textContent = error.message || String(error);
        errorBox.style.display = 'block';
      }
    }

    document.getElementById('password').addEventListener('keydown', (event) => {
      if (event.key === 'Enter') login();
    });
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html)


@app.post("/auth/login")
def login(payload: LoginRequest, request: Request, response: Response) -> dict:
    user = authenticate_user(payload.username, payload.password)

    if not user:
        write_audit_event(
            event_type="auth.login_failed",
            request=request,
            actor={"username": payload.username, "display_name": payload.username, "role": "unknown"},
            outcome="failure",
            target_type="auth",
            target_id=payload.username,
            metadata={"reason": "invalid_credentials"},
        )
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = create_session_token(user)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=session_ttl_seconds(),
        path="/",
    )

    write_audit_event(
        event_type="auth.login_success",
        request=request,
        actor=user,
        outcome="success",
        target_type="auth",
        target_id=user.get("username"),
        metadata={"role": user.get("role")},
    )

    return {
        "status": "ok",
        "user": user,
        "redirect": "/instructor",
    }


@app.post("/auth/logout")
def logout(request: Request, response: Response) -> dict:
    user = get_optional_user(request)
    write_audit_event(
        event_type="auth.logout",
        request=request,
        actor=user,
        outcome="success",
        target_type="auth",
        target_id=user.get("username") if user else "anonymous",
    )
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"status": "logged_out"}


@app.get("/auth/me")
def auth_me(user: dict = Depends(get_current_user)) -> dict:
    return user


@app.get("/auth/status")
def get_auth_status(user: dict = Depends(require_roles("admin"))) -> dict:
    return auth_status()



@app.get("/audit/status")
def get_audit_status(user: dict = Depends(require_roles("admin"))) -> dict:
    return audit_status()


@app.get("/audit/recent")
def get_recent_audit_events(
    limit: int = Query(default=50, ge=1, le=500),
    user: dict = Depends(require_roles("admin")),
) -> dict:
    return {
        "limit": limit,
        "events": read_recent_audit_events(limit=limit),
    }



@app.get("/instructor", response_class=HTMLResponse)
def instructor_panel(request: Request) -> HTMLResponse:
    user = get_optional_user(request)

    if not user:
        write_audit_event(
            event_type="panel.instructor_redirect_login",
            request=request,
            actor=None,
            outcome="redirect",
            target_type="panel",
            target_id="instructor",
        )
        return RedirectResponse(url="/login", status_code=303)

    if user.get("role") not in {"admin", "instructor"}:
        write_audit_event(
            event_type="panel.instructor_access_denied",
            request=request,
            actor=user,
            outcome="forbidden",
            target_type="panel",
            target_id="instructor",
            metadata={"role": user.get("role")},
        )
        raise HTTPException(status_code=403, detail="Instructor or admin role required.")

    write_audit_event(
        event_type="panel.instructor_access",
        request=request,
        actor=user,
        outcome="success",
        target_type="panel",
        target_id="instructor",
        metadata={"role": user.get("role")},
    )

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
        retrieved_context=to_context_items(kb_results),
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


@app.get("/sessions/{session_id}")
def get_session(session_id: str, user: dict = Depends(require_roles("admin", "instructor"))) -> dict:
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
def rebuild_kb(user: dict = Depends(require_roles("admin"))) -> dict:
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



@app.get("/lab-templates/status")
def get_lab_templates_status(user: dict = Depends(require_roles("admin", "instructor"))) -> dict:
    return lab_template_status()


@app.get("/lab-templates")
def list_lab_templates(user: dict = Depends(require_roles("admin", "instructor"))) -> dict:
    return {
        "templates": list_lab_template_summaries(),
    }


@app.get("/lab-templates/{template_id}")
def read_lab_template(
    template_id: str,
    request: Request,
    user: dict = Depends(require_roles("admin", "instructor")),
) -> dict:
    template = get_lab_template(template_id)

    if not template:
        write_audit_event(
            event_type="lab_template.read",
            request=request,
            actor=user,
            outcome="not_found",
            target_type="lab_template",
            target_id=template_id,
        )
        raise HTTPException(status_code=404, detail="Lab template not found.")

    write_audit_event(
        event_type="lab_template.read",
        request=request,
        actor=user,
        outcome="success",
        target_type="lab_template",
        target_id=template_id,
        metadata={
            "domain": template.get("domain"),
            "difficulty": template.get("difficulty"),
            "mentor_mode": template.get("mentor_mode"),
        },
    )

    return template


@app.post("/lab-templates/match")
def match_lab_template_endpoint(
    payload: dict,
    request: Request,
    user: dict = Depends(require_roles("admin", "instructor")),
) -> dict:
    text = str(payload.get("text", ""))
    result = match_lab_template(text)

    template = result.get("template") or {}

    write_audit_event(
        event_type="lab_template.match",
        request=request,
        actor=user,
        outcome="success" if result.get("matched") else "no_match",
        target_type="lab_template",
        target_id=template.get("template_id"),
        metadata={
            "matched": result.get("matched"),
            "score": result.get("score"),
            "matches": result.get("matches"),
            "template_id": template.get("template_id"),
            "domain": template.get("domain"),
        },
    )

    return result



@app.get("/llm/status")
def get_llm_status(user: dict = Depends(require_roles("admin", "instructor"))) -> dict:
    return llm_status()


@app.post("/mentor/analyze-ticket/llm-guidance")
def mentor_analyze_ticket_llm_guidance(request: AnalyzeTicketRequest, user: dict = Depends(require_roles("admin", "instructor"))) -> dict:
    deterministic = mentor_analyze_ticket(request)

    try:
        enhanced = enhance_guidance(
            deterministic_response=deterministic.mentor_response,
            next_action=deterministic.next_action,
            risk_level=deterministic.risk_level,
            retrieved_sources=deterministic.retrieved_sources,
            retrieved_context=[item.model_dump() for item in deterministic.retrieved_context],
        )
    except LLMClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return {
        "session_id": deterministic.session_id,
        "next_action": deterministic.next_action,
        "risk_level": deterministic.risk_level,
        "retrieved_sources": deterministic.retrieved_sources,
        "retrieved_context": deterministic.retrieved_context,
        "lab_template": deterministic.lab_template,
        "deterministic_response": deterministic.mentor_response,
        "llm": enhanced,
        "guardrail": "Deterministic fields are authoritative. LLM output is assistive only.",
    }


@app.post("/mentor/zammad/ticket-number/{ticket_number}/llm-guidance")
def mentor_zammad_ticket_number_llm_guidance(
    ticket_number: str,
    request: Request,
    user: dict = Depends(require_roles("admin", "instructor")),
) -> dict:
    deterministic = mentor_zammad_ticket_number_draft_guidance(ticket_number, request, user)

    try:
        enhanced = enhance_guidance(
            deterministic_response=deterministic.mentor_response,
            next_action=deterministic.next_action,
            risk_level=deterministic.risk_level,
            retrieved_sources=deterministic.retrieved_sources,
            retrieved_context=[item.model_dump() for item in deterministic.retrieved_context],
        )
    except LLMClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    write_audit_event(
        event_type="mentor.llm_guidance_requested",
        request=request,
        actor=user,
        outcome="success",
        target_type="zammad_ticket",
        target_id=str(ticket_number),
        metadata={
            "internal_ticket_id": deterministic.ticket_id,
            "ticket_number": deterministic.zammad_ticket["ticket"].get("number"),
            "next_action": deterministic.next_action,
            "risk_level": deterministic.risk_level,
            "llm_enabled": enhanced.get("llm_enabled"),
            "llm_provider": enhanced.get("provider"),
            "llm_model": enhanced.get("model"),
            "lab_template_id": (deterministic.lab_template or {}).get("template_id"),
            "lab_template_domain": (deterministic.lab_template or {}).get("domain"),
        },
    )

    return {
        "ticket_id": deterministic.ticket_id,
        "ticket_number": deterministic.zammad_ticket["ticket"].get("number"),
        "session_id": deterministic.session_id,
        "next_action": deterministic.next_action,
        "risk_level": deterministic.risk_level,
        "zammad_ticket": deterministic.zammad_ticket,
        "retrieved_sources": deterministic.retrieved_sources,
        "retrieved_context": deterministic.retrieved_context,
        "lab_template": deterministic.lab_template,
        "deterministic_response": deterministic.mentor_response,
        "llm": enhanced,
        "guardrail": "Deterministic fields are authoritative. LLM output is assistive only.",
    }


@app.get("/zammad/health")
def zammad_health() -> dict:
    try:
        return get_zammad_health()
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/zammad/tickets/{ticket_id}")
def zammad_ticket(ticket_id: int, user: dict = Depends(require_roles("admin", "instructor"))) -> dict:
    try:
        return get_ticket(ticket_id)
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/zammad/tickets/by-number/{ticket_number}")
def zammad_ticket_by_number(
    ticket_number: str,
    request: Request,
    user: dict = Depends(require_roles("admin", "instructor")),
) -> dict:
    try:
        ticket = get_ticket_by_number(ticket_number)
        write_audit_event(
            event_type="zammad.ticket_read_by_number",
            request=request,
            actor=user,
            outcome="success",
            target_type="zammad_ticket",
            target_id=str(ticket_number),
            metadata={
                "internal_ticket_id": ticket.get("id"),
                "ticket_number": ticket.get("number"),
                "state": ticket.get("state"),
                "article_count": ticket.get("article_count"),
            },
        )
        return ticket
    except ZammadClientError as exc:
        write_audit_event(
            event_type="zammad.ticket_read_by_number",
            request=request,
            actor=user,
            outcome="failure",
            target_type="zammad_ticket",
            target_id=str(ticket_number),
            metadata={"error": str(exc)},
        )
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/zammad/tickets/{ticket_id}/articles")
def zammad_ticket_articles(ticket_id: int, user: dict = Depends(require_roles("admin", "instructor"))) -> dict:
    try:
        return {
            "ticket_id": ticket_id,
            "articles": get_ticket_articles(ticket_id),
        }
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/mentor/zammad/ticket/{ticket_id}/draft-guidance", response_model=ZammadDraftGuidanceResponse)
def mentor_zammad_ticket_draft_guidance(ticket_id: int, user: dict = Depends(require_roles("admin", "instructor"))) -> ZammadDraftGuidanceResponse:
    try:
        ticket = get_ticket(ticket_id)
        articles = get_ticket_articles(ticket_id)
        return build_zammad_draft_guidance_response(ticket, articles)
    except ZammadClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/mentor/zammad/ticket-number/{ticket_number}/draft-guidance", response_model=ZammadDraftGuidanceResponse)
def mentor_zammad_ticket_number_draft_guidance(
    ticket_number: str,
    request: Request,
    user: dict = Depends(require_roles("admin", "instructor")),
) -> ZammadDraftGuidanceResponse:
    try:
        ticket = get_ticket_by_number(ticket_number)
        ticket_id = int(ticket.get("id"))
        articles = get_ticket_articles(ticket_id)
        response = build_zammad_draft_guidance_response(ticket, articles)
        write_audit_event(
            event_type="mentor.guidance_requested",
            request=request,
            actor=user,
            outcome="success",
            target_type="zammad_ticket",
            target_id=str(ticket_number),
            metadata={
                "internal_ticket_id": ticket_id,
                "ticket_number": ticket.get("number"),
                "next_action": response.next_action,
                "risk_level": response.risk_level,
                "retrieved_sources_count": len(response.retrieved_sources),
                "lab_template_id": (response.lab_template or {}).get("template_id"),
                "lab_template_domain": (response.lab_template or {}).get("domain"),
                "llm_provider": "not_used",
            },
        )
        return response
    except ZammadClientError as exc:
        write_audit_event(
            event_type="mentor.guidance_requested",
            request=request,
            actor=user,
            outcome="failure",
            target_type="zammad_ticket",
            target_id=str(ticket_number),
            metadata={"error": str(exc)},
        )
        raise HTTPException(status_code=502, detail=str(exc))
