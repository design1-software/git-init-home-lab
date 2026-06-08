import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from dotenv import load_dotenv
from fastapi import HTTPException, Request, status
from pydantic import BaseModel

load_dotenv("/opt/aria-ai-mentor/.env")

COOKIE_NAME = "aria_session"
SUPPORTED_ROLES = {"admin", "instructor", "student", "viewer"}


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthUser(BaseModel):
    username: str
    display_name: str
    role: str
    active: bool = True


def auth_enabled() -> bool:
    return os.getenv("ARIA_AUTH_ENABLED", "true").strip().lower() == "true"


def users_path() -> Path:
    return Path(os.getenv("ARIA_AUTH_USERS_PATH", "/opt/aria-ai-mentor/data/auth/users.json"))


def session_secret() -> str:
    secret = os.getenv("ARIA_SESSION_SECRET", "").strip()
    if not secret:
        raise HTTPException(status_code=500, detail="ARIA_SESSION_SECRET is not configured.")
    return secret


def session_ttl_seconds() -> int:
    return int(os.getenv("ARIA_SESSION_TTL_SECONDS", "28800"))


def load_users() -> Dict[str, Any]:
    path = users_path()
    if not path.exists():
        return {"users": []}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_users(payload: Dict[str, Any]) -> None:
    path = users_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    path.chmod(0o600)


def hash_password(password: str, iterations: int = 260000) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_raw, salt, expected_digest = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations_raw)
        actual_digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        ).hex()

        return hmac.compare_digest(actual_digest, expected_digest)
    except Exception:
        return False


def find_user(username: str) -> Optional[Dict[str, Any]]:
    normalized = username.strip().lower()
    for user in load_users().get("users", []):
        if str(user.get("username", "")).strip().lower() == normalized:
            return user
    return None


def public_user(user: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "username": user.get("username"),
        "display_name": user.get("display_name") or user.get("username"),
        "role": user.get("role"),
        "active": bool(user.get("active", True)),
    }


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = find_user(username)
    if not user:
        return None

    if not user.get("active", True):
        return None

    if user.get("role") not in SUPPORTED_ROLES:
        return None

    if not verify_password(password, str(user.get("password_hash", ""))):
        return None

    return public_user(user)


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def sign_payload(payload: Dict[str, Any]) -> str:
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    encoded_payload = _b64url_encode(payload_json)
    signature = hmac.new(
        session_secret().encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return f"{encoded_payload}.{_b64url_encode(signature)}"


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        encoded_payload, encoded_signature = token.split(".", 1)
        expected_signature = hmac.new(
            session_secret().encode("utf-8"),
            encoded_payload.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        provided_signature = _b64url_decode(encoded_signature)
        if not hmac.compare_digest(expected_signature, provided_signature):
            return None

        payload = json.loads(_b64url_decode(encoded_payload).decode("utf-8"))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None

        return payload
    except Exception:
        return None


def create_session_token(user: Dict[str, Any]) -> str:
    now = int(time.time())
    payload = {
        "sub": user["username"],
        "display_name": user.get("display_name") or user["username"],
        "role": user["role"],
        "iat": now,
        "exp": now + session_ttl_seconds(),
    }
    return sign_payload(payload)


def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    if not auth_enabled():
        return {
            "username": "auth-disabled",
            "display_name": "Auth Disabled",
            "role": "admin",
            "active": True,
        }

    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None

    payload = verify_token(token)
    if not payload:
        return None

    user = find_user(str(payload.get("sub", "")))
    if not user or not user.get("active", True):
        return None

    return public_user(user)


def get_current_user(request: Request) -> Dict[str, Any]:
    user = get_optional_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    return user


def require_roles(*roles: str) -> Callable[[Request], Dict[str, Any]]:
    allowed_roles = set(roles)

    def dependency(request: Request) -> Dict[str, Any]:
        user = get_current_user(request)
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user.get('role')} is not allowed for this action.",
            )
        return user

    return dependency


def auth_status() -> Dict[str, Any]:
    payload = load_users()
    users = payload.get("users", [])
    role_counts: Dict[str, int] = {}

    for user in users:
        role = str(user.get("role", "unknown"))
        role_counts[role] = role_counts.get(role, 0) + 1

    return {
        "auth_enabled": auth_enabled(),
        "users_configured": len(users),
        "role_counts": role_counts,
        "supported_roles": sorted(SUPPORTED_ROLES),
        "session_ttl_seconds": session_ttl_seconds(),
    }
