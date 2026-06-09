import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

SUBMISSIONS_DIR = Path("/opt/aria-ai-mentor/data/lab_submissions")
SUBMISSIONS_PATH = SUBMISSIONS_DIR / "submissions.json"

TEMPLATES_DIR = Path("/opt/aria-ai-mentor/data/lab_submission_templates")

VALID_STATUSES = {
    "submitted",
    "needs_more_evidence",
    "completed",
    "rejected",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_submission_store() -> None:
    SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    if not SUBMISSIONS_PATH.exists():
        SUBMISSIONS_PATH.write_text(json.dumps({"submissions": []}, indent=2), encoding="utf-8")
        SUBMISSIONS_PATH.chmod(0o600)


def load_submission_store() -> dict[str, Any]:
    ensure_submission_store()
    try:
        return json.loads(SUBMISSIONS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"submissions": []}


def save_submission_store(payload: dict[str, Any]) -> None:
    ensure_submission_store()
    SUBMISSIONS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    SUBMISSIONS_PATH.chmod(0o600)


def list_lab_submission_templates() -> list[dict[str, Any]]:
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    templates = []

    for path in sorted(TEMPLATES_DIR.glob("*.json")):
        try:
            template = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        templates.append(
            {
                "template_id": template.get("template_id"),
                "title": template.get("title"),
                "domain": template.get("domain"),
                "category": template.get("category"),
                "difficulty": template.get("difficulty"),
                "required_evidence": template.get("required_evidence", []),
            }
        )

    return templates


def get_lab_submission_template(template_id: str) -> Optional[dict[str, Any]]:
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    path = TEMPLATES_DIR / f"{template_id}.json"

    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def list_lab_submissions(
    *,
    student: Optional[str] = None,
    template_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    safe_limit = max(1, min(int(limit), 1000))
    payload = load_submission_store()
    submissions = payload.get("submissions", [])

    results = []
    for submission in submissions:
        if student and submission.get("student") != student:
            continue
        if template_id and submission.get("template_id") != template_id:
            continue
        if status and submission.get("status") != status:
            continue
        results.append(submission)

    results.sort(key=lambda item: item.get("updated_at_utc", ""), reverse=True)
    return results[:safe_limit]


def get_lab_submission(submission_id: str) -> Optional[dict[str, Any]]:
    payload = load_submission_store()

    for submission in payload.get("submissions", []):
        if submission.get("submission_id") == submission_id:
            return submission

    return None


def create_lab_submission(
    *,
    student: str,
    template_id: str,
    title: str,
    domain: str,
    category: str,
    evidence: str,
    reflection: str = "",
    commands_used: str = "",
    created_by: str = "",
) -> dict[str, Any]:
    now = utc_now()

    submission = {
        "submission_id": str(uuid4()),
        "student": student,
        "template_id": template_id,
        "title": title,
        "domain": domain,
        "category": category,
        "status": "submitted",
        "evidence": evidence,
        "reflection": reflection,
        "commands_used": commands_used,
        "created_by": created_by or student,
        "created_at_utc": now,
        "updated_at_utc": now,
    }

    payload = load_submission_store()
    payload.setdefault("submissions", []).append(submission)
    save_submission_store(payload)

    return submission


def update_lab_submission_status(
    submission_id: str,
    *,
    status: str,
    reviewed_by: str,
    review_note: str = "",
) -> Optional[dict[str, Any]]:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid lab submission status: {status}")

    payload = load_submission_store()
    now = utc_now()

    for submission in payload.get("submissions", []):
        if submission.get("submission_id") == submission_id:
            submission["status"] = status
            submission["updated_at_utc"] = now
            submission["reviewed_by"] = reviewed_by
            submission["reviewed_at_utc"] = now

            submission.setdefault("review_notes", []).append(
                {
                    "status": status,
                    "reviewed_by": reviewed_by,
                    "review_note": review_note,
                    "timestamp_utc": now,
                }
            )

            save_submission_store(payload)
            return submission

    return None
