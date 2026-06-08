# AI Mentor — Model Decision (Phase AI-4)

> **Decision status:** v1 remains API-capable and assistive-only. Local LLM remains deferred. As of Jun 8, 2026, the backend includes an assistive LLM integration layer, but the provider is disabled by default and deterministic mentor logic remains authoritative.

> **Source of truth for implementation status:** `docs/ai-mentor-implementation-status.md`

---

## Decision Summary

| Question | Decision |
|---|---|
| v1 model deployment | API-capable assistive layer |
| Deterministic mentor logic | Authoritative |
| Recommended provider | Claude remains preferred for production sessions |
| Current implemented provider path | OpenAI-compatible assistive client exists; provider disabled |
| Local LLM in v1 | No |
| Local LLM future path | Yes — deferred until platform is stable |
| Who hosts the app | ARIA VLAN 70, CT 120 |
| Who handles model inference | External API only when explicitly enabled |

---

## Current Implementation

The AI Mentor backend includes:

- deterministic mentor logic
- KB retrieval
- Zammad read-only ticket context
- instructor panel display
- assistive LLM endpoint layer
- provider switch through `.env`

Current safe default:

```text
ARIA_LLM_PROVIDER=disabled
```

This means an API key may exist in `.env`, but no LLM calls occur unless the provider is explicitly enabled.

---

## Authority Boundary

The LLM is never the source of truth for the training decision.

Deterministic ARIA Mentor decides:

- `next_action`
- `risk_level`
- retrieved sources
- validation/completion status
- Zammad read-only boundary
- safety boundaries

The LLM may only:

- improve wording
- improve coaching clarity
- improve instructor readability
- add non-spoiling coaching questions
- preserve the deterministic decision

The LLM must not:

- change `next_action`
- change `risk_level`
- invent sources
- recommend Zammad writeback
- recommend ticket closure, reassignment, or priority changes
- bypass guardrails
- give shortcut answers

---

## Why API-Based for v1

### Instruction-following quality

The AI Mentor's behavior depends on precise adherence to a complex system prompt — mentor persona, guardrails, evidence-first enforcement, Cisco-specific rules, escalation behavior, and student-vs-mentor content separation. API-based frontier models generally follow nuanced system prompts more reliably than local models that can comfortably run on ARIA without additional GPU resources.

A mentor that gives students the answer when it should not, forgets to ask for evidence, or skips rollback-before-config guidance fails at its core job. Instruction following is not a nice-to-have — it is the product.

### Infrastructure priority

ARIA's workload queue remains:

```text
1. Zammad ticketing platform
2. AI Mentor backend
3. Wazuh SIEM
4. Netdata / NetAlertX / ntfy
5. Active Directory lab VM
6. Future lab VMs and LXC containers
7. Future local inference only if justified
```

Adding local inference before the platform is stable would consume RAM and CPU, introduce latency, and complicate operations.

### Operational simplicity

API-capable means:

- no model weight management
- no inference server to operate
- no GPU/CPU tuning
- predictable quality when enabled
- clear separation between mentor orchestration and model inference

The backend handles prompt construction, retrieval, session logging, Zammad integration, auth, and guardrails. It does not manage model weights.

---

## Provider Direction

Claude remains the preferred production provider for the training mentor because of:

1. system prompt adherence
2. reasoning quality for diagnostic guidance
3. refusal behavior under student pressure

The current code includes an OpenAI-compatible assistive integration path because it was straightforward to implement and test behind the disabled provider switch. This does not change the preferred production provider decision. Before enabling any provider for live use, the provider must pass the guardrail validation suite.

---

## Activation Gate

Before enabling any live LLM provider:

```text
[ ] Audit/event logging implemented
[ ] Guardrail deployment tests executed and recorded
[ ] Provider-specific system prompt validated
[ ] Token/cost control reviewed
[ ] LLM output verified to preserve deterministic next_action/risk_level
[ ] Instructor approval model confirmed
[ ] Rollback path documented: set ARIA_LLM_PROVIDER=disabled and restart service
```

---

## Local LLM: Deferred — Not Abandoned

Local LLM is a legitimate future path.

### Why it is not v1

| Concern | Detail |
|---|---|
| Instruction following | Current small local models can drift on multi-constraint guardrails |
| Infrastructure burden | Ollama/model weights would compete with Zammad, Wazuh, AD, and lab workloads |
| Deployment sequencing | Core platform and cross-domain workflows must stabilize first |
| Quality risk | A mentor that leaks answers or skips evidence fails the training mission |

### When to revisit

Revisit local LLM when all of the following are true:

```text
[ ] ARIA workload stack is stable
[ ] Real student sessions have been validated
[ ] A local model passes guardrail testing
[ ] ARIA resource utilization leaves inference headroom
[ ] Privacy, cost, or offline operation justifies the complexity
```

### Candidate local models

| Model | Size | Notes |
|---|---|---|
| Mistral 7B Instruct | 7B | Fast on CPU, reasonable instruction following |
| LLaMA 3.x 8B Instruct | 8B | Strong small-model candidate |
| Phi family | small/medium | Good reasoning candidate; requires testing |
| Qwen Instruct | 7B/14B | Strong instruction-following candidate |

Serving path: Ollama on ARIA. No GPU assumed.

---

## Architecture Impact

```text
Current v1:
  ARIA hosts: FastAPI backend + JSONL retrieval + session logs + auth
  External: optional LLM API, disabled by default
  Deterministic mentor logic: authoritative

Future vector/LLM upgrade:
  ARIA hosts: FastAPI + ChromaDB/vector DB + optional local inference
  External: optional provider fallback
```

---

*Original decision date: Jun 4, 2026*
*Reconciled: Jun 8, 2026*
*Review trigger: audit logging complete + validated student sessions + guardrail tests recorded*
