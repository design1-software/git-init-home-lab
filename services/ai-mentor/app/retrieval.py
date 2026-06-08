import json
import re
from pathlib import Path
from typing import List, Dict, Any


KB_PATH = Path("/opt/aria-ai-mentor/data/kb/chunks.jsonl")
MANIFEST_PATH = Path("/opt/aria-ai-mentor/data/kb/manifest.json")


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_-]{3,}", text.lower()))


def load_chunks() -> List[Dict[str, Any]]:
    if not KB_PATH.exists():
        return []

    chunks = []
    with KB_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunks.append(json.loads(line))

    return chunks


def kb_status() -> Dict[str, Any]:
    chunks = load_chunks()

    manifest = {}
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    categories: dict[str, int] = {}
    for chunk in chunks:
        category = chunk.get("category", "unknown")
        categories[category] = categories.get(category, 0) + 1

    return {
        "status": "ready" if chunks else "empty",
        "chunks": len(chunks),
        "categories": categories,
        "manifest": manifest,
    }


def search_chunks(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    query_terms = tokenize(query)
    if not query_terms:
        return []

    scored = []

    for chunk in load_chunks():
        text = chunk.get("text", "")
        source_path = chunk.get("source_path", "")
        category = chunk.get("category", "")

        haystack_terms = tokenize(f"{source_path} {category} {text}")
        overlap = query_terms.intersection(haystack_terms)

        if not overlap:
            continue

        score = len(overlap)

        if "ticket-009" in source_path.lower():
            score += 3
        if "ai-mentor" in source_path.lower():
            score += 2
        if "runbook" in source_path.lower():
            score += 1

        scored.append(
            {
                "score": score,
                "chunk_id": chunk.get("chunk_id"),
                "source_path": source_path,
                "category": category,
                "chunk_index": chunk.get("chunk_index"),
                "preview": text[:500],
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]
