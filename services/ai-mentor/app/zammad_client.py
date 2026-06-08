import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv("/opt/aria-ai-mentor/.env")


class ZammadClientError(Exception):
    pass


def get_zammad_config() -> tuple[str, str]:
    base_url = os.getenv("ZAMMAD_BASE_URL", "").rstrip("/")
    token = os.getenv("ZAMMAD_API_TOKEN", "")

    if not base_url:
        raise ZammadClientError("ZAMMAD_BASE_URL is not configured.")

    if not token:
        raise ZammadClientError("ZAMMAD_API_TOKEN is not configured.")

    return base_url, token


def zammad_headers() -> dict:
    _, token = get_zammad_config()
    return {
        "Authorization": f"Token token={token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def zammad_get(path: str, params: Optional[dict] = None) -> Any:
    base_url, _ = get_zammad_config()
    url = f"{base_url}{path}"

    response = requests.get(
        url,
        headers=zammad_headers(),
        params=params or {},
        timeout=15,
    )

    if response.status_code >= 400:
        raise ZammadClientError(
            f"Zammad API error {response.status_code}: {response.text[:500]}"
        )

    return response.json()


def get_zammad_health() -> Dict[str, Any]:
    base_url = os.getenv("ZAMMAD_BASE_URL", "").rstrip("/")
    monitoring_token = os.getenv("ZAMMAD_MONITORING_TOKEN", "")

    if not base_url:
        raise ZammadClientError("ZAMMAD_BASE_URL is not configured.")

    if monitoring_token:
        url = f"{base_url}/api/v1/monitoring/health_check"
        response = requests.get(url, params={"token": monitoring_token}, timeout=15)
        if response.status_code >= 400:
            raise ZammadClientError(
                f"Zammad monitoring error {response.status_code}: {response.text[:500]}"
            )
        return response.json()

    groups = zammad_get("/api/v1/groups")
    return {
        "status": "ok",
        "method": "api_token_groups_check",
        "group_count": len(groups) if isinstance(groups, list) else None,
    }


def get_ticket(ticket_id: int) -> Dict[str, Any]:
    return zammad_get(f"/api/v1/tickets/{ticket_id}", params={"expand": "true"})


def get_ticket_articles(ticket_id: int) -> List[Dict[str, Any]]:
    result = zammad_get(f"/api/v1/ticket_articles/by_ticket/{ticket_id}")

    if isinstance(result, list):
        return result

    if isinstance(result, dict) and "articles" in result:
        return result["articles"]

    return []


def summarize_ticket_for_mentor(ticket: Dict[str, Any], articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    article_summaries = []

    for article in articles:
        article_summaries.append(
            {
                "id": article.get("id"),
                "from": article.get("from"),
                "to": article.get("to"),
                "subject": article.get("subject"),
                "body": article.get("body"),
                "created_at": article.get("created_at"),
                "type": article.get("type"),
                "sender": article.get("sender"),
            }
        )

    return {
        "ticket": {
            "id": ticket.get("id"),
            "number": ticket.get("number"),
            "title": ticket.get("title"),
            "state": ticket.get("state"),
            "priority": ticket.get("priority"),
            "group": ticket.get("group"),
            "customer": ticket.get("customer"),
            "owner": ticket.get("owner"),
            "created_at": ticket.get("created_at"),
            "updated_at": ticket.get("updated_at"),
        },
        "articles": article_summaries,
    }
