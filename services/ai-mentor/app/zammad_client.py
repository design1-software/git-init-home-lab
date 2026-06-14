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


def get_zammad_web_url() -> str:
    return os.getenv("ZAMMAD_WEB_URL", os.getenv("ZAMMAD_BASE_URL", "")).rstrip("/")


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


def search_ticket_by_number(ticket_number: str) -> List[Dict[str, Any]]:
    result = zammad_get(
        "/api/v1/tickets/search",
        params={"query": f"number:{ticket_number}", "expand": "true"},
    )
    return normalize_ticket_search_result(result)


def normalize_ticket_search_result(result: Any) -> List[Dict[str, Any]]:
    if isinstance(result, list):
        return result

    if isinstance(result, dict):
        if isinstance(result.get("tickets"), list):
            return result["tickets"]
        if isinstance(result.get("assets"), dict):
            tickets = result["assets"].get("Ticket")
            if isinstance(tickets, dict):
                return list(tickets.values())
        if isinstance(result.get("assets"), list):
            return result["assets"]

    return []


def search_tickets(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    result = zammad_get(
        "/api/v1/tickets/search",
        params={"query": query, "limit": limit, "expand": "true"},
    )
    return normalize_ticket_search_result(result)


def ticket_identity(ticket: Dict[str, Any]) -> str:
    return str(ticket.get("id") or ticket.get("number") or "")


def normalize_student_ticket(ticket: Dict[str, Any]) -> Dict[str, Any]:
    web_url = get_zammad_web_url()
    number = str(ticket.get("number") or "")
    internal_id = ticket.get("id")
    ticket_url = f"{web_url}/#ticket/zoom/{internal_id}" if web_url and internal_id else ""

    return {
        "id": internal_id,
        "number": number,
        "title": ticket.get("title") or f"Zammad Ticket {number or internal_id}",
        "state": ticket.get("state"),
        "priority": ticket.get("priority"),
        "group": ticket.get("group"),
        "customer": ticket.get("customer"),
        "owner": ticket.get("owner"),
        "created_at": ticket.get("created_at"),
        "updated_at": ticket.get("updated_at"),
        "url": ticket_url,
    }


def get_student_tickets(zammad_login: str, limit: int = 25) -> List[Dict[str, Any]]:
    login = str(zammad_login or "").strip()
    if not login:
        return []

    queries = [f"owner:{login}", f"customer:{login}", f"{login}"]
    tickets_by_id: Dict[str, Dict[str, Any]] = {}

    for query in queries:
        try:
            for ticket in search_tickets(query=query, limit=limit):
                identity = ticket_identity(ticket)
                if identity:
                    tickets_by_id[identity] = ticket
        except ZammadClientError:
            continue

    tickets = [normalize_student_ticket(ticket) for ticket in tickets_by_id.values()]
    tickets.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
    return tickets[:limit]


def get_ticket_by_number(ticket_number: str) -> Dict[str, Any]:
    matches = search_ticket_by_number(ticket_number)
    exact_matches = [ticket for ticket in matches if str(ticket.get("number")) == str(ticket_number)]

    if not exact_matches:
        raise ZammadClientError(f"No Zammad ticket found for ticket number {ticket_number}.")

    if len(exact_matches) > 1:
        raise ZammadClientError(f"Multiple Zammad tickets found for ticket number {ticket_number}.")

    ticket_id = exact_matches[0].get("id")
    if ticket_id is None:
        raise ZammadClientError(f"Ticket number {ticket_number} was found but has no internal ID.")

    return get_ticket(int(ticket_id))


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
            "url": f"{get_zammad_web_url()}/#ticket/zoom/{ticket.get('id')}" if get_zammad_web_url() and ticket.get("id") else "",
        },
        "articles": article_summaries,
    }


def zammad_post(path: str, payload: dict) -> Any:
    base_url, _ = get_zammad_config()
    url = f"{base_url}{path}"

    response = requests.post(
        url,
        headers={**zammad_headers(), "Content-Type": "application/json"},
        json=payload,
        timeout=10,
    )

    if response.status_code >= 400:
        raise ZammadClientError(
            f"Zammad POST {path} failed with HTTP {response.status_code}: {response.text[:500]}"
        )

    if not response.text.strip():
        return {}

    return response.json()


def create_zammad_ticket(
    *,
    title: str,
    customer: str,
    body: str,
    group: str | None = None,
    priority: str = "2 normal",
    state: str = "new",
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if not title.strip():
        raise ZammadClientError("Cannot create a Zammad ticket without a title.")
    if not customer.strip():
        raise ZammadClientError("Cannot create a Zammad ticket without a customer.")
    if not body.strip():
        raise ZammadClientError("Cannot create a Zammad ticket without a body.")

    payload: Dict[str, Any] = {
        "title": title.strip(),
        "group": group or os.getenv("ZAMMAD_DEFAULT_GROUP", "Users"),
        "customer": customer.strip(),
        "state": state,
        "priority": priority,
        "article": {
            "subject": title.strip(),
            "body": body.strip(),
            "type": "note",
            "internal": False,
            "content_type": "text/plain",
        },
    }

    if tags:
        payload["tags"] = tags

    result = zammad_post("/api/v1/tickets", payload)

    return {
        "id": result.get("id"),
        "number": result.get("number"),
        "title": result.get("title") or title,
        "group": result.get("group") or payload.get("group"),
        "customer": result.get("customer") or customer,
        "state": result.get("state") or state,
        "priority": result.get("priority") or priority,
        "url": f"{get_zammad_web_url()}/#ticket/zoom/{result.get('id')}" if get_zammad_web_url() and result.get("id") else "",
    }


def create_zammad_ticket_note(ticket_id: int, body: str) -> Dict[str, Any]:
    if not body.strip():
        raise ZammadClientError("Cannot write an empty Zammad note.")

    payload = {
        "ticket_id": ticket_id,
        "type": "note",
        "sender": "Agent",
        "body": body,
        "content_type": "text/plain",
        "internal": False,
    }

    result = zammad_post("/api/v1/ticket_articles", payload)

    return {
        "ticket_id": ticket_id,
        "article_id": result.get("id"),
        "type": result.get("type") or "note",
        "internal": result.get("internal", False),
    }
