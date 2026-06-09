import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

ASSIGNMENTS_DIR = Path("/opt/aria-ai-mentor/data/assignments")
ASSIGNMENTS_PATH = ASSIGNMENTS_DIR / "assignments.json"

VALID_STATUSES = {
    "assigned",
    "in_progress",
    "submitted",
    "completed",
    "cancelled",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_store() -> None:
    ASSIGNMENTS_DIR.mkdir(parents=True, exist_ok=True)
    if not ASSIGNMENTS_PATH.exists():
        ASSIGNMENTS_PATH.write_text(json.dumps({"assignments": []}, indent=2), encoding="utf-8")
        ASSIGNMENTS_PATH.chmod(0o600)


def load_assignment_store() -> dict[str, Any]:
    ensure_store()
    try:
        return json.loads(ASSIGNMENTS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"assignments": []}


def save_assignment_store(payload: dict[str, Any]) -> None:
    ensure_store()
    ASSIGNMENTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    ASSIGNMENTS_PATH.chmod(0o600)


def list_assignments(
    student: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    safe_limit = max(1, min(int(limit), 1000))
    payload = load_assignment_store()
    assignments = payload.get("assignments", [])

    results = []
    for assignment in assignments:
        if student and assignment.get("student") != student:
            continue
        if status and assignment.get("status") != status:
            continue
        results.append(assignment)

    results.sort(key=lambda item: item.get("updated_at_utc", ""), reverse=True)
    return results[:safe_limit]


def get_assignment(assignment_id: str) -> Optional[dict[str, Any]]:
    payload = load_assignment_store()
    for assignment in payload.get("assignments", []):
        if assignment.get("assignment_id") == assignment_id:
            return assignment
    return None


def create_assignment(
    *,
    student: str,
    ticket_id: str,
    title: str,
    created_by: str,
    domain: str = "helpdesk",
    difficulty: str = "beginner",
    scenario: str = "",
    zammad_ticket_number: Optional[str] = None,
    zammad_ticket_id: Optional[str] = None,
    due_date: Optional[str] = None,
    notes: str = "",
) -> dict[str, Any]:
    now = utc_now()

    assignment = {
        "assignment_id": str(uuid4()),
        "student": student,
        "ticket_id": str(ticket_id),
        "title": title,
        "domain": domain,
        "difficulty": difficulty,
        "scenario": scenario,
        "zammad_ticket_number": zammad_ticket_number,
        "zammad_ticket_id": zammad_ticket_id,
        "status": "assigned",
        "due_date": due_date,
        "notes": notes,
        "created_by": created_by,
        "created_at_utc": now,
        "updated_at_utc": now,
    }

    payload = load_assignment_store()
    payload.setdefault("assignments", []).append(assignment)
    save_assignment_store(payload)

    return assignment


def update_assignment_status(
    assignment_id: str,
    *,
    status: str,
    updated_by: str,
    note: str = "",
) -> Optional[dict[str, Any]]:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid assignment status: {status}")

    payload = load_assignment_store()
    now = utc_now()

    for assignment in payload.get("assignments", []):
        if assignment.get("assignment_id") == assignment_id:
            assignment["status"] = status
            assignment["updated_at_utc"] = now
            assignment["updated_by"] = updated_by

            if note:
                assignment.setdefault("status_notes", []).append(
                    {
                        "note": note,
                        "status": status,
                        "updated_by": updated_by,
                        "timestamp_utc": now,
                    }
                )

            save_assignment_store(payload)
            return assignment

    return None


def mark_assignment_approved(
    assignment_id: str,
    *,
    approved_by: str,
    payload_hash: str,
    zammad_article_id: Optional[str] = None,
    note: str = "",
) -> Optional[dict[str, Any]]:
    payload = load_assignment_store()
    now = utc_now()

    for assignment in payload.get("assignments", []):
        if assignment.get("assignment_id") == assignment_id:
            assignment["status"] = "completed"
            assignment["updated_at_utc"] = now
            assignment["updated_by"] = approved_by
            assignment["approved_by"] = approved_by
            assignment["approved_at_utc"] = now
            assignment["approval"] = {
                "approved_by": approved_by,
                "approved_at_utc": now,
                "payload_hash": payload_hash,
                "zammad_article_id": zammad_article_id,
                "note": note,
            }
            assignment.setdefault("status_notes", []).append(
                {
                    "note": note or "Instructor approved writeback and marked assignment completed.",
                    "status": "completed",
                    "updated_by": approved_by,
                    "timestamp_utc": now,
                    "payload_hash": payload_hash,
                    "zammad_article_id": zammad_article_id,
                }
            )

            save_assignment_store(payload)
            return assignment

    return None
