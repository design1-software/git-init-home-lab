#!/usr/bin/env python3
"""Create a Zammad lab ticket and matching ARIA assignment.

Run this inside CT 120 after the AI Mentor app is deployed.
"""

import argparse
from pathlib import Path
import sys

APP_ROOT = Path("/opt/aria-ai-mentor/app")
if str(APP_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(APP_ROOT.parent))

from app.assignment_store import create_assignment  # noqa: E402
from app.lab_templates import get_lab_template  # noqa: E402
from app.student_profile import get_student_profile  # noqa: E402
from app.zammad_client import create_zammad_ticket  # noqa: E402


def normalize_template_id(value: str) -> str:
    raw = str(value or "").strip().lower()
    if raw.endswith(".json"):
        raw = raw[:-5]
    if raw.startswith("ticket-"):
        parts = raw.split("-")
        if len(parts) >= 2 and parts[1].isdigit():
            return f"ticket-{parts[1].zfill(3)}"
    return raw


def ticket_id_from_template_id(template_id: str) -> str:
    normalized = normalize_template_id(template_id)
    if normalized.startswith("ticket-"):
        parts = normalized.split("-")
        if len(parts) >= 2 and parts[1].isdigit():
            return parts[1].zfill(3)
    return normalized


def format_required_evidence(template: dict) -> str:
    lines = []
    for item in template.get("required_evidence", []) or []:
        label = item.get("label") or item.get("id") or "Evidence"
        description = item.get("description") or item.get("prompt") or ""
        lines.append(f"- {label}: {description}" if description else f"- {label}")
    return "\n".join(lines) if lines else "- Instructor-defined evidence requirements apply."


def build_ticket_body(template: dict, profile: dict, extra_instructions: str) -> str:
    target_lines = []
    for target in profile.get("target_systems", []) or []:
        name = target.get("name") or "Assigned target"
        access = target.get("access") or "See instructor"
        purpose = target.get("purpose") or "Run assigned lab commands"
        target_lines.append(f"- {name}: {access} ({purpose})")

    return f"""ARIA Help Desk Training Ticket

Lab:
{template.get('template_id')} - {template.get('title')}

Scenario:
{template.get('summary') or 'Review the issue, collect evidence, and document the result.'}

Required Evidence:
{format_required_evidence(template)}

Open:
1. Zammad - read and document the ticket.
2. ARIA AI Mentor - load this ticket and validate evidence.
3. Assigned lab target system - run the actual troubleshooting commands.

Assigned Target System:
{chr(10).join(target_lines) if target_lines else '- Target system will be provided by instructor.'}

Rules:
- Do not close the ticket.
- Do not guess or invent output.
- Paste real command output into ARIA AI Mentor.
- Draft the final note in ARIA and wait for instructor review.

Instructor Notes:
{extra_instructions.strip() or 'None'}
""".strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Zammad lab ticket and ARIA assignment.")
    parser.add_argument("--student", required=True, help="ARIA student username, such as student02")
    parser.add_argument("--template", required=True, help="Lab template ID or filename, such as ticket-001 or ticket-001-dns-failure")
    parser.add_argument("--customer", default=None, help="Optional Zammad customer lookup value, such as the student's Zammad email/login")
    parser.add_argument("--created-by", default="instructor", help="Instructor username for local assignment audit field")
    parser.add_argument("--group", default=None, help="Optional Zammad group override")
    parser.add_argument("--priority", default="2 normal", help="Zammad priority, default: 2 normal")
    parser.add_argument("--due-date", default=None, help="Optional due date text for ARIA assignment")
    parser.add_argument("--extra", default="", help="Optional instructor notes")
    args = parser.parse_args()

    profile = get_student_profile(args.student)
    zammad_customer = args.customer or profile.get("zammad_login") or args.student
    requested_template = args.template
    normalized_template = normalize_template_id(requested_template)
    template = get_lab_template(normalized_template)
    if template is None:
        print(f"ERROR: Lab template not found: {requested_template}", file=sys.stderr)
        print(f"Tried normalized template id: {normalized_template}", file=sys.stderr)
        return 1

    title = f"{template.get('template_id')}: {template.get('title')}"
    body = build_ticket_body(template, profile, args.extra)

    zammad_ticket = create_zammad_ticket(
        title=title,
        customer=str(zammad_customer),
        body=body,
        group=args.group,
        priority=args.priority,
    )

    assignment = create_assignment(
        student=args.student,
        ticket_id=ticket_id_from_template_id(str(template.get("template_id") or normalized_template)),
        title=title,
        created_by=args.created_by,
        domain=str(template.get("domain") or "helpdesk"),
        difficulty=str(template.get("difficulty") or "beginner"),
        scenario=body,
        zammad_ticket_number=str(zammad_ticket.get("number") or ""),
        zammad_ticket_id=str(zammad_ticket.get("id") or ""),
        due_date=args.due_date,
        notes=f"Created by ARIA lab ticket creation script. Zammad customer lookup: {zammad_customer}",
    )

    print("Zammad ticket created and ARIA assignment linked.")
    print(f"Zammad customer lookup: {zammad_customer}")
    print(f"Zammad ticket number: {zammad_ticket.get('number')}")
    print(f"Zammad ticket id: {zammad_ticket.get('id')}")
    print(f"Zammad URL: {zammad_ticket.get('url')}")
    print(f"Assignment ID: {assignment.get('assignment_id')}")
    print(f"Student: {assignment.get('student')}")
    print(f"Lab ticket ID: {assignment.get('ticket_id')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
