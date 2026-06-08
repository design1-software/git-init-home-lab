import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv("/opt/aria-ai-mentor/.env")


class LLMClientError(Exception):
    pass


def get_llm_config() -> Dict[str, Any]:
    provider = os.getenv("ARIA_LLM_PROVIDER", "disabled").strip().lower()
    model = os.getenv("ARIA_LLM_MODEL", "gpt-4.1").strip()
    max_output_tokens = int(os.getenv("ARIA_LLM_MAX_OUTPUT_TOKENS", "800"))

    return {
        "provider": provider,
        "model": model,
        "max_output_tokens": max_output_tokens,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY", "").strip()),
    }


def llm_status() -> Dict[str, Any]:
    config = get_llm_config()

    return {
        "status": "disabled" if config["provider"] == "disabled" else "configured",
        "provider": config["provider"],
        "model": config["model"],
        "openai_configured": config["openai_configured"],
        "mode": "assistive_only",
        "guardrail": "LLM may enhance wording but cannot change next_action, risk_level, retrieved_sources, or Zammad state.",
    }


def build_llm_prompt(
    deterministic_response: str,
    next_action: str,
    risk_level: str,
    retrieved_sources: List[str],
    retrieved_context: List[dict],
) -> str:
    source_lines = "\n".join(f"- {source}" for source in retrieved_sources) or "- none"

    context_lines = []
    for item in retrieved_context[:5]:
        context_lines.append(
            f"Source: {item.get('source_path')} | Category: {item.get('category')} | "
            f"Chunk: {item.get('chunk_index')} | Score: {item.get('score')}\n"
            f"Preview: {item.get('preview')}"
        )

    context_text = "\n\n".join(context_lines) or "No retrieved context."

    return f"""
You are ARIA Mentor, an evidence-first IT training coach.

Your job:
- Improve clarity and coaching quality.
- Keep the student focused on evidence, documentation, and next-step thinking.
- Do not give shortcuts.
- Do not contradict the deterministic mentor result.
- Do not change next_action.
- Do not change risk_level.
- Do not invent sources.
- Do not recommend Zammad writeback, closure, reassignment, priority changes, or automation.
- If the ticket is complete, keep the completion message clear and concise.
- If the ticket is incomplete, ask coaching questions instead of giving away answers.

Deterministic next_action:
{next_action}

Deterministic risk_level:
{risk_level}

Retrieved sources:
{source_lines}

Retrieved context:
{context_text}

Deterministic mentor response:
{deterministic_response}

Return an improved instructor-facing ARIA Mentor guidance message.
""".strip()


def enhance_with_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise LLMClientError("OPENAI_API_KEY is not configured.")

    config = get_llm_config()

    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": config["model"],
            "input": prompt,
            "max_output_tokens": config["max_output_tokens"],
            "store": False,
        },
        timeout=45,
    )

    if response.status_code >= 400:
        raise LLMClientError(f"OpenAI API error {response.status_code}: {response.text[:500]}")

    payload = response.json()

    if "output_text" in payload:
        return str(payload["output_text"]).strip()

    output_items = payload.get("output", [])
    text_parts = []

    for item in output_items:
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                text_parts.append(content.get("text", ""))

    enhanced = "\n".join(part for part in text_parts if part).strip()
    if not enhanced:
        raise LLMClientError("OpenAI response did not contain text output.")

    return enhanced


def enhance_guidance(
    deterministic_response: str,
    next_action: str,
    risk_level: str,
    retrieved_sources: List[str],
    retrieved_context: List[dict],
) -> Dict[str, Any]:
    config = get_llm_config()

    if config["provider"] == "disabled":
        return {
            "llm_enabled": False,
            "provider": "disabled",
            "model": config["model"],
            "enhanced_response": deterministic_response,
            "note": "LLM provider is disabled. Returned deterministic mentor response.",
        }

    prompt = build_llm_prompt(
        deterministic_response=deterministic_response,
        next_action=next_action,
        risk_level=risk_level,
        retrieved_sources=retrieved_sources,
        retrieved_context=retrieved_context,
    )

    if config["provider"] == "openai":
        enhanced = enhance_with_openai(prompt)
        return {
            "llm_enabled": True,
            "provider": "openai",
            "model": config["model"],
            "enhanced_response": enhanced,
            "note": "LLM enhanced guidance generated. Deterministic decision fields remain authoritative.",
        }

    raise LLMClientError(f"Unsupported ARIA_LLM_PROVIDER: {config['provider']}")
