from typing import Any, Dict, List, Tuple
import re

from app.models import AnalyzeTicketRequest


COMPLETION_PHRASES = [
    "resolution summary",
    "zammad v1 platform validation passed",
    "ticket-009 confirms the basic training-ticket workflow",
]


def normalize_for_detection(text: str) -> str:
    normalized = text.lower()
    normalized = re.sub(r"<[^>]+>", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def ticket_009_is_complete(text: str) -> bool:
    normalized = normalize_for_detection(text)
    return all(phrase in normalized for phrase in COMPLETION_PHRASES)


def format_sources(kb_results: List[Dict[str, Any]]) -> str:
    if not kb_results:
        return "No KB source was retrieved for this request."

    lines = []
    for index, item in enumerate(kb_results[:3], start=1):
        lines.append(
            f"{index}. {item.get('source_path')} "
            f"(category: {item.get('category')}, chunk: {item.get('chunk_index')}, score: {item.get('score')})"
        )
    return "\n".join(lines)


def unique_sources(kb_results: List[Dict[str, Any]]) -> List[str]:
    sources = []
    for item in kb_results:
        source = item.get("source_path")
        if source and source not in sources:
            sources.append(source)
    return sources


def build_ticket_009_completion_response(
    request: AnalyzeTicketRequest,
    kb_results: List[Dict[str, Any]],
) -> Tuple[str, str, str, List[str]]:
    sources_text = format_sources(kb_results)
    retrieved_sources = unique_sources(kb_results)

    if not retrieved_sources:
        retrieved_sources = ["labs/helpdesk/ticket-009-zammad-ticket-triage.md"]

    mentor_response = f"""--- ARIA Mentor ---

Situation Summary:
Ticket-009 appears complete.

Source Context Used:
{sources_text}

Validation Observed:
1. Student accessed the ticket.
2. Student added an update.
3. Resolution summary is present.
4. Ticket workflow validation was documented.

Next Step:
Instructor can mark this lab as complete and capture the portfolio output.

--- End ---"""
    return mentor_response, "low", "validation_complete", retrieved_sources


def build_ticket_009_response(
    request: AnalyzeTicketRequest,
    kb_results: List[Dict[str, Any]],
) -> Tuple[str, str, str, List[str]]:
    evidence = (request.student_evidence or "").strip()
    sources_text = format_sources(kb_results)
    retrieved_sources = unique_sources(kb_results)

    if not retrieved_sources:
        retrieved_sources = ["labs/helpdesk/ticket-009-zammad-ticket-triage.md"]

    combined_ticket_text = f"{request.ticket_title}\n{request.ticket_body}\n{evidence}"

    if ticket_009_is_complete(combined_ticket_text):
        return build_ticket_009_completion_response(request, kb_results)

    if not evidence:
        mentor_response = f"""--- ARIA Mentor ---

Situation Summary:
You are working on Ticket-{request.ticket_id}, a basic ARIA Help Desk ticket workflow validation.

Source Context Used:
{sources_text}

What I need to see:
1. Confirm that you can open the ticket.
2. Add a comment describing what the ticket is asking you to do.
3. Add one sentence explaining what evidence proves the workflow is working.

Why this matters:
In real help desk work, the ticket is the operational record. A useful ticket update helps the next technician, the instructor, and the customer understand what happened.

Evidence Standard:
Do not just write "done." A professional ticket update should describe what you saw, what you did, and what the result was.

Next Step:
Post a short professional update in the ticket, then provide that update as evidence.

--- End ---"""
        return mentor_response, "low", "student_update_required", retrieved_sources

    mentor_response = f"""--- ARIA Mentor ---

Situation Summary:
You provided evidence for Ticket-{request.ticket_id}: {evidence}

Source Context Used:
{sources_text}

Assessment:
This evidence is appropriate for a beginner help desk workflow validation if it confirms ticket access, ticket visibility, commenting, and update history.

What I need to see next:
1. Confirm whether the instructor/admin can see your comment.
2. Confirm whether the ticket can be closed with a clear resolution summary.
3. Write one professional closure sentence.

Suggested Closure Language:
"Zammad ticket workflow validated. I was able to access the ticket, review the request, add a comment, and confirm the ticket history captured the update."

Why this matters:
A ticket is not complete just because the task was performed. It is complete when the work is documented clearly enough for another person to understand what happened.

Next Step:
Add the closure summary and ask the instructor to verify and close the ticket.

--- End ---"""
    return mentor_response, "low", "closure_summary_required", retrieved_sources


def analyze_ticket(
    request: AnalyzeTicketRequest,
    kb_results: List[Dict[str, Any]] | None = None,
) -> Tuple[str, str, str, List[str]]:
    kb_results = kb_results or []
    normalized_title = request.ticket_title.lower()
    retrieved_sources = unique_sources(kb_results)

    if request.ticket_id in {"009", "4"} or "zammad ticket triage" in normalized_title:
        return build_ticket_009_response(request, kb_results)

    sources_text = format_sources(kb_results)

    mentor_response = f"""--- ARIA Mentor ---

Situation Summary:
This ticket type is not fully mapped yet.

Source Context Used:
{sources_text}

What I need to see:
1. State the issue in one sentence.
2. Provide the exact evidence you have.
3. Explain what you think the next step should be.

Why this matters:
ARIA Mentor requires evidence before diagnosis. Do not jump to a fix without confirming what is actually happening.

Next Step:
Add ticket evidence and classify the issue domain.

--- End ---"""
    return mentor_response, "low", "evidence_required", retrieved_sources
