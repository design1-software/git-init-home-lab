import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


DEFAULT_INCLUDE_DIRS = [
    "docs",
    "labs",
]

DEFAULT_EXCLUDE_PARTS = [
    ".git",
    ".env",
    "node_modules",
    "__pycache__",
    ".venv",
    "secrets",
    "credentials",
    "private",
]


def should_exclude(path: Path) -> bool:
    path_str = str(path).lower()
    return any(part in path_str for part in DEFAULT_EXCLUDE_PARTS)


def iter_markdown_files(repo_root: Path, include_dirs: List[str]) -> Iterable[Path]:
    for include_dir in include_dirs:
        base = repo_root / include_dir
        if not base.exists():
            continue

        for path in base.rglob("*.md"):
            if path.is_file() and not should_exclude(path):
                yield path


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, max_chars: int = 1800, overlap_chars: int = 250) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []

    sections = re.split(r"(?=^#{1,4}\s+)", text, flags=re.MULTILINE)

    chunks = []
    current = ""

    for section in sections:
        section = section.strip()
        if not section:
            continue

        if len(current) + len(section) + 2 <= max_chars:
            current = f"{current}\n\n{section}".strip()
        else:
            if current:
                chunks.append(current)
            current = section

            while len(current) > max_chars:
                chunk = current[:max_chars]
                chunks.append(chunk.strip())
                current = current[max_chars - overlap_chars :]

    if current:
        chunks.append(current.strip())

    return chunks


def stable_chunk_id(source_path: str, chunk_index: int, text: str) -> str:
    digest = hashlib.sha256(f"{source_path}:{chunk_index}:{text[:200]}".encode("utf-8")).hexdigest()
    return digest[:16]


def infer_category(relative_path: str) -> str:
    lower = relative_path.lower()

    if lower.startswith("labs/helpdesk"):
        return "helpdesk_lab"
    if lower.startswith("labs"):
        return "lab"
    if "ai-mentor" in lower:
        return "ai_mentor"
    if "runbook" in lower or "runbooks" in lower:
        return "runbook"
    if "zammad" in lower:
        return "ticketing"
    if "network" in lower or "vlan" in lower or "cisco" in lower:
        return "network"
    if "proxmox" in lower:
        return "proxmox"
    if lower.startswith("docs"):
        return "documentation"

    return "general"


def ingest(repo_root: Path, output_path: Path) -> dict:
    repo_root = repo_root.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    records = []
    markdown_files = list(iter_markdown_files(repo_root, DEFAULT_INCLUDE_DIRS))

    for md_file in markdown_files:
        relative_path = str(md_file.relative_to(repo_root))
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        chunks = chunk_text(text)

        for index, chunk in enumerate(chunks):
            record = {
                "chunk_id": stable_chunk_id(relative_path, index, chunk),
                "source_path": relative_path,
                "chunk_index": index,
                "category": infer_category(relative_path),
                "text": chunk,
                "char_count": len(chunk),
                "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            records.append(record)

    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    manifest = {
        "repo_root": str(repo_root),
        "output_path": str(output_path),
        "files_scanned": len(markdown_files),
        "chunks_written": len(records),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    manifest_path = output_path.parent / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest ARIA Markdown docs into local JSONL KB chunks.")
    parser.add_argument(
        "--repo-root",
        default="/opt/aria-ai-mentor/source/git-init-home-lab",
        help="Path to local git-init-home-lab repository clone.",
    )
    parser.add_argument(
        "--output",
        default="/opt/aria-ai-mentor/data/kb/chunks.jsonl",
        help="Output JSONL path.",
    )
    args = parser.parse_args()

    manifest = ingest(Path(args.repo_root), Path(args.output))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
