# ARIA AI Mentor Backend

This service provides the backend foundation for the ARIA AI Mentor.

The AI Mentor is designed to coach IT students through evidence-first troubleshooting, ticket discipline, documentation, escalation logic, and lab workflow. It must not operate as a shortcut machine.

## Current Status

Phase: backend foundation

Implemented:

- FastAPI app skeleton
- systemd deployment on CT 120 `aria-ai-mentor-01`
- `/health`
- `/mentor/analyze-ticket`
- `/sessions/{session_id}`
- local JSON session logging
- deterministic Ticket-009 mentor logic
- markdown knowledge-base ingestion
- `/kb/status`
- `/kb/search`
- `/kb/rebuild`

Not yet implemented:

- vector embeddings
- LLM provider integration
- Zammad API integration
- instructor draft panel
- automated Zammad internal-note writeback

## Runtime Location

Production-like lab deployment path on CT 120:

```bash
/opt/aria-ai-mentor
```

## Local Run

```bash
cd /opt/aria-ai-mentor
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8081
```

Health check:

```bash
curl http://localhost:8081/health
```

Swagger UI:

```text
http://192.168.70.30:8081/docs
```

## Knowledge Base

The KB ingestion script clones or reads the ARIA home lab repo from:

```bash
/opt/aria-ai-mentor/source/git-init-home-lab
```

It ingests approved markdown from:

```text
docs/
labs/
```

It writes:

```bash
/opt/aria-ai-mentor/data/kb/chunks.jsonl
/opt/aria-ai-mentor/data/kb/manifest.json
```

Rebuild:

```bash
python scripts/ingest_docs.py
```

or through the API:

```bash
curl -X POST http://localhost:8081/kb/rebuild
```

## Account Model Note

Zammad uses email-based login identifiers. ARIA Linux/container usernames are tracked separately in ticket/user notes and lab documentation.

Example:

```text
Linux/container username: sprather
Zammad login: sprath11@wgu.edu
Zammad display name: Sha Neal Prather
```
