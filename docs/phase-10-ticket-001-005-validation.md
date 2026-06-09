# Phase 10 — Ticket-001 through Ticket-005 Workflow Validation

> **Purpose:** Validate that ARIA Mentor correctly supports the first five help desk ticket workflows without losing existing Field-Tech, CCNA, or troubleshooting lab domains.
>
> **Status:** Complete. Validated on CT 120 `aria-ai-mentor-01` on Jun 9, 2026.

---

## Scope

Phase 10 validates mentor-supported workflows for:

| Ticket | Lab file | Expected template | Expected primary domain | Validation status |
|---|---|---|---|---|
| Ticket-001 | `labs/helpdesk/ticket-001-dns-failure.md` | `ticket-001` | DNS | Pass |
| Ticket-002 | `labs/helpdesk/ticket-002-vlan-misassignment.md` | `ticket-002` | Switching | Pass |
| Ticket-003 | `labs/helpdesk/ticket-003-proxmox-apt-egress-failure.md` | `ticket-003` | Linux | Pass |
| Ticket-004 | `labs/helpdesk/ticket-004-ssh-legacy-kex.md` | `ticket-004` | Security | Pass |
| Ticket-005 | `labs/helpdesk/ticket-005-vlan1-return-path-failure.md` | `ticket-005` | Networking | Pass |

---

## Domain Protection Rule

Phase 10 is limited to Help Desk Tickets 001-005.

It must not overwrite or de-prioritize:

- `labs/field-tech/` production student labs
- Sha-Neal Prather's completed Field-Tech Lab 001 history
- Field-Tech Lab 002 production training content
- CCNA/networking labs under `labs/lab-*.md`
- Troubleshooting labs under `labs/troubleshooting-*.md`

Reference inventory:

```text
docs/aria-training-lab-inventory.md
```

---

## Deployment Steps Used on CT 120

Run from CT 120: `aria-ai-mentor-01`.

> Note: CT 120 is accessed as `root`; `sudo` is not installed and is not required.

```bash
cd /opt/aria-ai-mentor/source/git-init-home-lab
git pull origin main

cp services/ai-mentor/app/mentor_engine.py /opt/aria-ai-mentor/app/mentor_engine.py
cp -r services/ai-mentor/lab_templates /opt/aria-ai-mentor/

systemctl restart aria-ai-mentor
systemctl status aria-ai-mentor --no-pager
```

Service health validated:

```bash
curl -s http://127.0.0.1:8081/health | jq
```

Observed:

```json
{
  "status": "ok",
  "service": "aria-ai-mentor",
  "hostname": "aria-ai-mentor-01",
  "mode": "local-dev"
}
```

KB rebuild performed after pulling new docs:

```bash
cd /opt/aria-ai-mentor
/opt/aria-ai-mentor/.venv/bin/python /opt/aria-ai-mentor/scripts/ingest_docs.py
systemctl restart aria-ai-mentor
curl -s http://127.0.0.1:8081/kb/status | jq
```

Observed rebuild output:

```json
{
  "repo_root": "/opt/aria-ai-mentor/source/git-init-home-lab",
  "output_path": "/opt/aria-ai-mentor/data/kb/chunks.jsonl",
  "files_scanned": 48,
  "chunks_written": 297,
  "timestamp_utc": "2026-06-09T04:31:21.094228+00:00"
}
```

---

## Validation Standard

Each ticket must pass these checks:

```text
[x] Correct lab template is matched
[x] Correct domain is returned in lab_template metadata
[x] Mentor response includes template-aware guidance
[x] Required evidence is shown
[x] Missing evidence returns request_more_evidence where tested
[x] Complete evidence returns validation_complete
[x] Retrieved sources include the related lab file and/or lab_template source
[x] Student is coached without shortcut answers
[x] Existing field-tech lab inventory remains untouched
```

---

## Test 1 — Ticket-001 DNS Failure

### Missing evidence test

```bash
curl -s -X POST http://127.0.0.1:8081/mentor/analyze-ticket \
  -H 'Content-Type: application/json' \
  -d '{
    "ticket_id": "001",
    "student": "phase10-test",
    "domain": "helpdesk",
    "difficulty": "beginner",
    "ticket_title": "Ticket-001: DNS Resolution Failing",
    "ticket_body": "Client is connected to WiFi but websites are not loading.",
    "student_evidence": ""
  }' | jq
```

Observed result:

```text
session_id = b09a6c00-c5dc-4b8c-8489-5c80970bf4b8
lab_template.template_id = ticket-001
lab_template.domain = dns
next_action = request_more_evidence
retrieved_sources includes labs/helpdesk/ticket-001-dns-failure.md
retrieved_sources includes lab_template:ticket-001
mentor_response includes Required Evidence
```

### Complete evidence test

```bash
curl -s -X POST http://127.0.0.1:8081/mentor/analyze-ticket \
  -H 'Content-Type: application/json' \
  -d '{
    "ticket_id": "001",
    "student": "phase10-test",
    "domain": "helpdesk",
    "difficulty": "beginner",
    "ticket_title": "Ticket-001: DNS Resolution Failing",
    "ticket_body": "Client is connected to WiFi but websites are not loading.",
    "student_evidence": "ping 8.8.8.8 succeeds. ping google.com fails. nslookup google.com fails. DNS server from ipconfig is 192.168.10.16. Client DNS configuration verified."
  }' | jq
```

Observed result:

```text
session_id = 0548084a-44b8-4f4e-bb94-63692d230e58
lab_template.template_id = ticket-001
lab_template.domain = dns
next_action = validation_complete
Evidence Detected:
1. IP connectivity test
2. DNS query result
3. Client DNS configuration
Evidence Still Needed = No missing evidence detected
```

Status: **Pass**

---

## Test 2 — Ticket-002 VLAN Misassignment

```bash
curl -s -X POST http://127.0.0.1:8081/mentor/analyze-ticket \
  -H 'Content-Type: application/json' \
  -d '{
    "ticket_id": "002",
    "student": "phase10-test",
    "domain": "helpdesk",
    "difficulty": "beginner",
    "ticket_title": "Ticket-002: Device on Wrong VLAN",
    "ticket_body": "Device is connected to Gorgeous-IoT but received the wrong subnet.",
    "student_evidence": "SSID is Gorgeous-IoT. Device received 192.168.100.25, which indicates VLAN 1. Expected VLAN is VLAN 30 / 192.168.30.0. AP port switchport membership was checked with show interfaces status and VLAN membership."
  }' | jq
```

Observed result:

```text
session_id = efec15cb-bb62-4078-8241-60c57a80549f
lab_template.template_id = ticket-002
lab_template.domain = switching
next_action = validation_complete
Evidence Detected:
1. Switchport or SSID status
2. Assigned VLAN or observed subnet
3. Expected VLAN
Evidence Still Needed = No missing evidence detected
```

Status: **Pass**

---

## Test 3 — Ticket-003 Proxmox APT Egress Failure

```bash
curl -s -X POST http://127.0.0.1:8081/mentor/analyze-ticket \
  -H 'Content-Type: application/json' \
  -d '{
    "ticket_id": "003",
    "student": "phase10-test",
    "domain": "helpdesk",
    "difficulty": "beginner",
    "ticket_title": "Ticket-003: Proxmox Host Cannot Run apt update",
    "ticket_body": "Proxmox apt update fails with network or repository errors.",
    "student_evidence": "apt update shows Network is unreachable. ping -c 3 8.8.8.8 succeeds. ping download.proxmox.com and DNS resolution were tested. Gateway and internet reachability test completed."
  }' | jq
```

Observed result:

```text
session_id = 1fd6b9f3-b0b3-4e38-af6a-826116531ce9
lab_template.template_id = ticket-003
lab_template.domain = linux
next_action = validation_complete
Evidence Detected:
1. APT error output
2. DNS test
3. Gateway or internet reachability test
Evidence Still Needed = No missing evidence detected
```

Status: **Pass**

---

## Test 4 — Ticket-004 SSH Legacy KEX

```bash
curl -s -X POST http://127.0.0.1:8081/mentor/analyze-ticket \
  -H 'Content-Type: application/json' \
  -d '{
    "ticket_id": "004",
    "student": "phase10-test",
    "domain": "helpdesk",
    "difficulty": "intermediate",
    "ticket_title": "Ticket-004: SSH Legacy KEX Negotiation",
    "ticket_body": "Student cannot SSH into the Cisco switch but can ping it.",
    "student_evidence": "SSH error message says no matching key exchange method found. ssh -v output shows their offer includes diffie-hellman-group14-sha1 and ssh-rsa. This is a legacy temporary workaround and a security risk; long-term remediation is device upgrade or stronger SSH algorithms."
  }' | jq
```

Observed result:

```text
session_id = 3b7c856e-0ec2-4684-9791-d507a0496707
lab_template.template_id = ticket-004
lab_template.domain = security
next_action = validation_complete
Evidence Detected:
1. SSH error message
2. Verbose SSH output
3. Security risk statement
Evidence Still Needed = No missing evidence detected
```

Status: **Pass**

---

## Test 5 — Ticket-005 VLAN 1 Return Path Failure

```bash
curl -s -X POST http://127.0.0.1:8081/mentor/analyze-ticket \
  -H 'Content-Type: application/json' \
  -d '{
    "ticket_id": "005",
    "student": "phase10-test",
    "domain": "helpdesk",
    "difficulty": "intermediate",
    "ticket_title": "Ticket-005: VLAN 1 Return Path Failure",
    "ticket_body": "ARIA can reach gateway and DNS but internet pings fail during transitional topology.",
    "student_evidence": "Source is ARIA 192.168.100.10 and destination is 8.8.8.8. Gateway ping -c 3 192.168.100.1 succeeds. nslookup works. ip route get shows default path. show ip route 192.168.100.0 on C1111 and source vlan 1 testing indicate return path asymmetric routing. show ip nat translations reviewed."
  }' | jq
```

Observed result:

```text
session_id = 8fa4cbc6-56d9-4b61-b0df-670da41f1ae5
lab_template.template_id = ticket-005
lab_template.domain = networking
next_action = validation_complete
Evidence Detected:
1. Source and destination
2. Forward path evidence
3. Return path evidence
Evidence Still Needed = No missing evidence detected
```

Status: **Pass**

---

## Audit Validation

The direct `/mentor/analyze-ticket` endpoint is currently unauthenticated and does not create the same audit footprint as authenticated Zammad guidance routes.

Audit metadata for `lab_template_id` and `lab_template_domain` remains validated for authenticated Zammad guidance routes from Phase 9C. Future student-facing routes should add explicit student mentor access audit events.

---

## Phase 10 Completion Gate

Phase 10 completion status:

```text
[x] Ticket-001 missing-evidence and complete-evidence tests pass
[x] Ticket-002 complete-evidence test passes
[x] Ticket-003 complete-evidence test passes
[x] Ticket-004 complete-evidence test passes
[x] Ticket-005 complete-evidence test passes
[x] Template metadata is returned for all five tickets
[x] next_action behavior is acceptable
[x] KB retrieval returns relevant lab context
[x] No field-tech lab content was moved, overwritten, or reclassified
[x] docs/aria-training-lab-inventory.md remains aligned with repo reality
```

Phase 10 is complete.

---

## Next Phase After Completion

After Phase 10 is complete, proceed to:

```text
Phase 11 — Student-Facing Mentor Panel v1
```

Do not begin Phase 11 until Phase 10 validation evidence is captured.
