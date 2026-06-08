#!/usr/bin/env python3
"""
ARIA AI Mentor -- Knowledge Base Ingestion Script

Reads approved docs from the ARIA repo, splits them into heading-bounded
chunks, and writes data/kb/chunks.jsonl for keyword retrieval by the
AI Mentor backend.

Usage:
    python3 scripts/ingest_docs.py [repo_root]

Default repo_root: /opt/aria-ai-mentor/repo
Output:           data/kb/chunks.jsonl (relative to repo_root)

Run after any documentation update to rebuild the knowledge base.
The output file is gitignored -- it is generated, not committed.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Approved knowledge sources
# File paths are relative to repo root.
# ---------------------------------------------------------------------------
APPROVED_FILES = [
    "README.md",
    "ROADMAP.md",
    "docs/vlan-design.md",
    "docs/network-quick-reference.md",
    "docs/proxmox-server-build.md",
    "docs/monitoring-architecture.md",
    "docs/ai-mentor-architecture.md",
    "docs/ai-mentor-knowledge-base-plan.md",
    "docs/ai-mentor-guardrails-expanded.md",
    "docs/ai-mentor-ticketing-integration.md",
    "docs/ai-mentor-model-decision.md",
    "docs/runbooks/config-backup.md",
    "docs/runbooks/cisco/vlan1-temporary-host-routes.md",
    "docs/runbooks/aria-student-container-provisioning.md",
    "docs/runbooks/zammad/zammad-lxc-deployment.md",
    "labs/field-tech/sha-neal-roadmap.md",
]

# Glob patterns -- these are processed after APPROVED_FILES
APPROVED_GLOBS = [
    "labs/helpdesk/ticket-*.md",
    "labs/field-tech/**/instructor-notes.md",
    "labs/lab-*.md",
    "docs/runbooks/**/*.md",
]

# ---------------------------------------------------------------------------
# Never include -- student-facing content, secrets, non-IT material
# Any source path containing one of these substrings is skipped.
# ---------------------------------------------------------------------------
EXCLUDED_SUBSTRINGS = [
    "student-guide.md",   # student branch content -- would spoil discovery
    "social-media-mcp",
    ".env",
]

OUTPUT_PATH = "data/kb/chunks.jsonl"


def chunk_by_headings(text: str, source_file: str) -> list:
    """Split a markdown document into heading-bounded chunks.

    Each heading starts a new chunk. The chunk includes the heading line
    and all content until the next heading. Chunks with no meaningful
    content are discarded.
    """
    chunks = []
    current_lines = []
    current_heading = "(top)"
    chunk_index = 0
    now = datetime.now(timezone.utc).isoformat()

    for line in text.splitlines():
        is_heading = line.startswith("#") and line.lstrip("#").strip()
        if is_heading:
            # Flush current chunk
            content = "\n".join(current_lines).strip()
            if content:
                chunk_id = hashlib.md5(
                    f"{source_file}:{chunk_index}".encode()
                ).hexdigest()[:8]
                chunks.append({
                    "chunk_id": chunk_id,
                    "source": source_file,
                    "heading": current_heading,
                    "content": content,
                    "indexed_at": now,
                })
                chunk_index += 1
            current_heading = line.lstrip("#").strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    # Flush final chunk
    content = "\n".join(current_lines).strip()
    if content:
        chunk_id = hashlib.md5(
            f"{source_file}:{chunk_index}".encode()
        ).hexdigest()[:8]
        chunks.append({
            "chunk_id": chunk_id,
            "source": source_file,
            "heading": current_heading,
            "content": content,
            "indexed_at": now,
        })

    return chunks


def is_excluded(source_str: str) -> bool:
    return any(excl in source_str for excl in EXCLUDED_SUBSTRINGS)


def ingest(repo_root: str) -> int:
    repo = Path(repo_root)
    output = repo / OUTPUT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)

    all_chunks = []
    seen: set = set()

    def process(filepath: Path) -> None:
        source = str(filepath.relative_to(repo))
        if source in seen:
            return
        if is_excluded(source):
            print(f"  [-] {source} -- excluded")
            return
        seen.add(source)
        if not filepath.exists():
            print(f"  [!] {source} -- not found, skipping")
            return
        text = filepath.read_text(encoding="utf-8")
        chunks = chunk_by_headings(text, source)
        all_chunks.extend(chunks)
        print(f"  [+] {source} -> {len(chunks)} chunks")

    print("Processing approved files...")
    for rel in APPROVED_FILES:
        process(repo / rel)

    print("\nProcessing glob patterns...")
    for pattern in APPROVED_GLOBS:
        for fp in sorted(repo.glob(pattern)):
            process(fp)

    print(f"\nWriting {len(all_chunks)} chunks to {OUTPUT_PATH} ...")
    with open(output, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"KB rebuild complete -- {len(all_chunks)} chunks written.")
    return len(all_chunks)


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "/opt/aria-ai-mentor/repo"
    print(f"Ingesting docs from: {root}\n")
    total = ingest(root)
    print(f"\nTotal: {total} chunks")
