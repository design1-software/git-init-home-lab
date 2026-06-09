import json
from pathlib import Path
from typing import Optional

from app.models import SessionRecord

SESSIONS_DIR = Path("/opt/aria-ai-mentor/data/sessions")
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def save_session(record: SessionRecord) -> Path:
    path = SESSIONS_DIR / f"{record.session_id}.json"
    path.write_text(record.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_session(session_id: str) -> Optional[dict]:
    path = SESSIONS_DIR / f"{session_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_sessions(limit: int = 500) -> list[dict]:
    """Return recent saved mentor sessions, newest first."""
    safe_limit = max(1, min(int(limit), 2000))
    records: list[dict] = []

    for session_path in sorted(SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:safe_limit]:
        try:
            records.append(json.loads(session_path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            records.append({
                "session_id": session_path.stem,
                "malformed": True,
                "path": str(session_path),
            })

    return records
