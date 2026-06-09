import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv("/opt/aria-ai-mentor/.env")

DEFAULT_TEMPLATE_DIR = "/opt/aria-ai-mentor/lab_templates"


def template_dir() -> Path:
    return Path(os.getenv("ARIA_LAB_TEMPLATE_DIR", DEFAULT_TEMPLATE_DIR))


def _load_template_file(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        template = json.load(file)

    required = ["template_id", "title", "domain", "difficulty", "ticket_type", "mentor_mode"]
    missing = [field for field in required if not template.get(field)]

    if missing:
        raise ValueError(f"{path.name} missing required fields: {', '.join(missing)}")

    template["_source_file"] = str(path)
    return template


def load_lab_templates() -> List[Dict[str, Any]]:
    directory = template_dir()

    if not directory.exists():
        return []

    templates: List[Dict[str, Any]] = []

    for path in sorted(directory.glob("*.json")):
        templates.append(_load_template_file(path))

    return templates


def lab_template_status() -> Dict[str, Any]:
    templates = load_lab_templates()

    return {
        "template_dir": str(template_dir()),
        "templates_loaded": len(templates),
        "template_ids": [template["template_id"] for template in templates],
        "domains": sorted({template.get("domain", "unknown") for template in templates}),
    }


def list_lab_template_summaries() -> List[Dict[str, Any]]:
    summaries = []

    for template in load_lab_templates():
        summaries.append(
            {
                "template_id": template.get("template_id"),
                "title": template.get("title"),
                "domain": template.get("domain"),
                "difficulty": template.get("difficulty"),
                "ticket_type": template.get("ticket_type"),
                "mentor_mode": template.get("mentor_mode"),
                "status": template.get("status", "unknown"),
                "summary": template.get("summary", ""),
            }
        )

    return summaries


def get_lab_template(template_id: str) -> Optional[Dict[str, Any]]:
    wanted = template_id.strip().lower()

    for template in load_lab_templates():
        if str(template.get("template_id", "")).lower() == wanted:
            return template

    return None


def match_lab_template(text: str) -> Dict[str, Any]:
    haystack = (text or "").lower()
    best_template: Optional[Dict[str, Any]] = None
    best_score = 0
    best_matches: List[str] = []

    for template in load_lab_templates():
        matches = []

        for term in template.get("trigger_terms", []):
            term_text = str(term).strip().lower()
            if term_text and term_text in haystack:
                matches.append(term)

        score = len(matches)

        if score > best_score:
            best_score = score
            best_template = template
            best_matches = matches

    return {
        "matched": best_template is not None,
        "score": best_score,
        "matches": best_matches,
        "template": best_template,
    }


def build_lab_template_context(match_result: Dict[str, Any]) -> Dict[str, Any]:
    template = match_result.get("template") or {}

    if not match_result.get("matched") or not template:
        return {
            "matched": False,
            "score": match_result.get("score", 0),
            "matches": match_result.get("matches", []),
        }

    return {
        "matched": True,
        "score": match_result.get("score", 0),
        "matches": match_result.get("matches", []),
        "template_id": template.get("template_id"),
        "title": template.get("title"),
        "domain": template.get("domain"),
        "difficulty": template.get("difficulty"),
        "mentor_mode": template.get("mentor_mode"),
        "required_evidence": template.get("required_evidence", []),
        "opening_questions": template.get("opening_questions", []),
        "completion_signals": template.get("completion_signals", []),
        "mentor_guidance_rules": template.get("mentor_guidance_rules", []),
        "next_actions": template.get("next_actions", {}),
    }


def append_template_guidance(mentor_response: str, lab_template: Dict[str, Any]) -> str:
    if not lab_template.get("matched"):
        return mentor_response

    evidence_lines = []
    for item in lab_template.get("required_evidence", []):
        label = item.get("label", "")
        description = item.get("description", "")
        if label and description:
            evidence_lines.append(f"- {label}: {description}")
        elif label:
            evidence_lines.append(f"- {label}")

    question_lines = [f"- {question}" for question in lab_template.get("opening_questions", [])]
    signal_lines = [f"- {signal}" for signal in lab_template.get("completion_signals", [])]

    sections = [
        mentor_response.strip(),
        "",
        "Matched Lab Template",
        f"- Template: {lab_template.get('template_id')} — {lab_template.get('title')}",
        f"- Domain: {lab_template.get('domain')}",
        f"- Difficulty: {lab_template.get('difficulty')}",
        f"- Mentor mode: {lab_template.get('mentor_mode')}",
    ]

    if evidence_lines:
        sections.extend(["", "Required Evidence", *evidence_lines])

    if question_lines:
        sections.extend(["", "Opening Coaching Questions", *question_lines])

    if signal_lines:
        sections.extend(["", "Completion Signals", *signal_lines])

    sections.extend([
        "",
        "Template Guardrail",
        "Use the template to coach and validate evidence. Do not give shortcut answers or mark the lab complete without the required evidence.",
    ])

    return "\n".join(sections).strip()
