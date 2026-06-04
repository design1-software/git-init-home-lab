# AI Mentor — Model Decision (Phase AI-4)

> **Decision locked:** v1 = API-based LLM. Local LLM = research/future path only.

---

## Decision Summary

| Question | Decision |
|---|---|
| v1 model deployment | API-based |
| Recommended provider | Claude (Anthropic) |
| Local LLM in v1 | No |
| Local LLM future path | Yes — deferred until platform is stable |
| Who hosts the app | ARIA (VLAN 70) |
| Who handles the model | External API |

---

## Why API-Based for v1

### Instruction-following quality

The AI Mentor's behavior depends entirely on precise adherence to a complex system prompt — mentor persona, guardrails, evidence-first enforcement, Cisco-specific rules, escalation behavior, student-vs-mentor content separation. API-based frontier models (Claude, GPT-4o) follow nuanced system prompts reliably. Current local models at the 7B–13B parameter range that can run on ARIA's hardware do not.

A mentor that occasionally gives students the answer when it shouldn't, or forgets to ask for evidence, or skips the rollback-before-config step, fails at its core job. Instruction following is not a nice-to-have — it is the product.

### Infrastructure priority

ARIA's first workload queue (in order):

```
1. Zammad (ticketing platform)
2. AI Mentor backend (FastAPI + ChromaDB)
3. Wazuh SIEM
4. Netdata / NetAlertX / ntfy
5. Active Directory lab VM
6. Future: additional lab VMs and LXC containers
```

Adding a local LLM inference server (Ollama + a 7B+ model) to this list before the platform is stable would consume significant RAM and CPU, introduce GPU-less quantized inference latency, and complicate the VLAN 70 deployment. ARIA has 64GB DDR5 and a Ryzen 9 7900X — capable, but first the platform needs to be built and tested under real workloads before adding inference overhead.

### Operational simplicity

API-based means:
- No model management (weights, updates, quantization)
- No inference server to operate
- No GPU/CPU tuning
- No context window management at the infrastructure level
- Predictable latency and quality

The AI Mentor backend handles: prompt construction, knowledge base retrieval, session logging, Zammad integration. It does not handle: model weights, inference, batching. Keeping these concerns separate is correct architecture for v1.

### Cost at lab scale

Lab-scale usage (one instructor, occasional student sessions) generates a small number of API calls per day. At frontier model pricing, this is negligible — measured in cents per session, not dollars. This is not a cost driver at this scale.

Cost becomes a consideration only if the platform grows to serve many concurrent students at high frequency. That is a future problem.

---

## Recommended Provider: Claude

Claude is recommended over alternatives for this use case for three specific reasons:

**1. System prompt adherence**
Claude follows complex, multi-constraint system prompts more consistently than alternatives at equivalent model tiers. The guardrails in `docs/ai-mentor-guardrails-expanded.md` are extensive — they require a model that respects them reliably, not one that drifts under pressure.

**2. Reasoning quality for diagnostic guidance**
IT troubleshooting guidance requires multi-step reasoning: understanding what a symptom implies, what evidence would confirm or refute a hypothesis, and what the next single step should be. Claude's reasoning quality at this task is strong.

**3. Refusal behavior**
When a student asks the mentor to just give them the answer, or to bypass a guardrail, the model must decline clearly and redirect — not comply or give a hedged version of the answer. Claude's refusal behavior on instruction-following tasks is well-calibrated for this.

### API model recommendation

Use the latest available Claude Sonnet tier for production sessions. Reserve Opus for complex multi-step diagnostic scenarios if quality gaps appear. Haiku is too small for reliable guardrail adherence in this context.

---

## Local LLM: Deferred — Not Abandoned

Local LLM is a legitimate future path, documented here so the decision is revisitable with clear criteria.

### Why it was not chosen for v1

| Concern | Detail |
|---|---|
| Instruction following | Current 7B–13B local models drift on complex multi-constraint system prompts |
| Infrastructure burden | Ollama + model weights compete with Zammad, Wazuh, and lab VMs on ARIA |
| Deployment sequencing | ARIA VLAN 70 cutover has not happened yet — adding inference before the base is stable is premature |
| Quality risk | A mentor that leaks answers or skips guardrails fails the training mission |

### When to revisit

Revisit local LLM when ALL of the following are true:

```
[ ] ARIA is stable on VLAN 70 with full workload stack running
[ ] Platform has been validated with real student sessions (API-based v1)
[ ] A local model demonstrates acceptable guardrail adherence in testing
[ ] ARIA resource utilization leaves headroom for inference
[ ] There is a specific reason (privacy, cost, offline operation) that justifies the complexity
```

### Candidate local models (for future evaluation)

| Model | Size | Notes |
|---|---|---|
| Mistral 7B Instruct | 7B | Fast on CPU, reasonable instruction following |
| LLaMA 3.1 8B Instruct | 8B | Meta's strongest small model for instruction tasks |
| Phi-3 Medium | 14B | Microsoft, strong on reasoning tasks, heavier |
| Qwen2.5 14B Instruct | 14B | Strong instruction following at 14B tier |

Serving: Ollama on ARIA. No GPU — CPU inference only. At 7B quantized (Q4), expect 10–30 tokens/second on the Ryzen 9 7900X. This is usable for a single-session lab but not for concurrent students.

---

## Architecture Impact of This Decision

```
v1 (API-based):
  ARIA hosts: FastAPI backend + ChromaDB + session logs
  External: LLM API (Claude)
  ARIA RAM for inference: 0 GB

Future local option:
  ARIA hosts: FastAPI + ChromaDB + Ollama + model weights (~4–8GB for 7B Q4)
  External: nothing
  ARIA RAM for inference: 6–10 GB additional
```

v1 architecture is documented in `docs/ai-mentor-architecture.md` and `docs/ai-mentor-ticketing-integration.md`.

---

*Decision date: Jun 4, 2026*
*Review trigger: Platform stable on VLAN 70 + validated student sessions*
