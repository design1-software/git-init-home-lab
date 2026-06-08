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
