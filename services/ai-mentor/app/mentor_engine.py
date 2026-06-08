from app.models import AnalyzeTicketRequest


def build_ticket_009_response(request: AnalyzeTicketRequest) -> tuple[str, str, str, list[str]]:
    evidence = (request.student_evidence or "").strip()

    if not evidence:
        mentor_response = """--- ARIA Mentor ---

Situation Summary:
You are working on a basic ARIA Help Desk ticket workflow validation.

What I need to see:
1. Confirm that you can open the ticket.
2. Add a comment describing what the ticket is asking you to do.
3. Add one sentence explaining what evidence proves the workflow is working.

Why this matters:
In real help desk work, the ticket is the operational record. A useful ticket update helps the next technician, the instructor, and the customer understand what happened.

Next Step:
Post a short professional update in the ticket. Do not just write "done."

--- End ---"""
        return mentor_response, "low", "student_update_required", [
            "labs/helpdesk/ticket-009-zammad-ticket-triage.md"
        ]

    mentor_response = f"""--- ARIA Mentor ---

Situation Summary:
You provided evidence for Ticket-{request.ticket_id}: {evidence}

Assessment:
This is appropriate for a beginner help desk workflow validation if it confirms ticket access, visibility, commenting, and update history.

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
    return mentor_response, "low", "closure_summary_required", [
        "labs/helpdesk/ticket-009-zammad-ticket-triage.md"
    ]


def analyze_ticket(request: AnalyzeTicketRequest) -> tuple[str, str, str, list[str]]:
    normalized_title = request.ticket_title.lower()

    if request.ticket_id == "009" or "zammad ticket triage" in normalized_title:
        return build_ticket_009_response(request)

    mentor_response = """--- ARIA Mentor ---

Situation Summary:
This ticket type is not fully mapped yet.

What I need to see:
1. State the issue in one sentence.
2. Provide the exact evidence you have.
3. Explain what you think the next step should be.

Why this matters:
ARIA Mentor requires evidence before diagnosis. Do not jump to a fix without confirming what is actually happening.

Next Step:
Add ticket evidence and classify the issue domain.

--- End ---"""
    return mentor_response, "low", "evidence_required", []
