import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import Request

load_dotenv("/opt/aria-ai-mentor/.env")

DEFAULT_AUDIT_PATH = "/opt/aria-ai-mentor/data/audit/events.jsonl"
SENSITIVE_KEYS = {
    "password",
    "token",
    "cookie",
    "authorization",
    "api_key",
    "openai_api_key",
    "anthropic_api_key",
    "session",
    "secret",
}


def audit_path() -> Path:
    return Path(os.getenv("ARIA_AUDIT_LOG_PATH", DEFAULT_AUDIT_PATH))


def audit_enabled() -> bool:
    return os.getenv("ARIA_AUDIT_ENABLED", "true").strip().lower() == "true"


def _client_ip(request: Optional[Request]) -> Optional[str]:
    if not request or not request.client:
        return None
    return request.client.host


def _safe_actor(actor: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not actor:
        return {
            "username": "anonymous",
            "display_name": "Anonymous",
            "role": "anonymous",
        }

    return {
        "username": actor.get("username", "unknown"),
        "display_name": actor.get("display_name", actor.get("username", "unknown")),
        "role": actor.get("role", "unknown"),
    }


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return sanitize_metadata(value)

    if isinstance(value, list):
        return [_sanitize_value(item) for item in value[:25]]

    if isinstance(value, str):
        if len(value) > 500:
            return value[:500] + "...[truncated]"
        return value

    return value


def sanitize_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not metadata:
        return {}

    clean: Dict[str, Any] = {}

    for key, value in metadata.items():
        key_text = str(key)
        key_lower = key_text.lower()

        if any(sensitive in key_lower for sensitive in SENSITIVE_KEYS):
            clean[key_text] = "[redacted]"
        else:
            clean[key_text] = _sanitize_value(value)

    return clean


def write_audit_event(
    event_type: str,
    request: Optional[Request] = None,
    actor: Optional[Dict[str, Any]] = None,
    outcome: str = "success",
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "actor": _safe_actor(actor),
        "client_ip": _client_ip(request),
        "method": request.method if request else None,
        "path": str(request.url.path) if request else None,
        "outcome": outcome,
        "target_type": target_type,
        "target_id": target_id,
        "metadata": sanitize_metadata(metadata),
    }

    if not audit_enabled():
        return event

    path = audit_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, separators=(",", ":"), sort_keys=True) + "\n")

    path.chmod(0o600)
    return event


def read_recent_audit_events(limit: int = 50) -> list[Dict[str, Any]]:
    path = audit_path()

    if not path.exists():
        return []

    safe_limit = max(1, min(int(limit), 500))

    with path.open("r", encoding="utf-8") as file:
        lines = file.readlines()[-safe_limit:]

    events = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append({"malformed": True, "raw": line[:500]})

    return events


def audit_status() -> Dict[str, Any]:
    path = audit_path()

    if not path.exists():
        return {
            "audit_enabled": audit_enabled(),
            "path": str(path),
            "exists": False,
            "size_bytes": 0,
            "events": 0,
        }

    events = 0
    with path.open("r", encoding="utf-8") as file:
        for _ in file:
            events += 1

    return {
        "audit_enabled": audit_enabled(),
        "path": str(path),
        "exists": True,
        "size_bytes": path.stat().st_size,
        "events": events,
    }
