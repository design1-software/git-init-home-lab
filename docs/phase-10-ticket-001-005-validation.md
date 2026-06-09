# Phase 10 — Ticket-001 through Ticket-005 Workflow Validation

> **Purpose:** Validate that ARIA Mentor correctly supports the first five help desk ticket workflows without losing existing Field-Tech, CCNA, or troubleshooting lab domains.
>
> **Status:** Validation runbook created during Phase 10.

---

## Scope

Phase 10 validates mentor-supported workflows for:

| Ticket | Lab file | Expected template | Expected primary domain |
|---|---|---|---|
| Ticket-001 | `labs/helpdesk/ticket-001-dns-failure.md` | `ticket-001` | DNS |
| Ticket-002 | `labs/helpdesk/ticket-002-vlan-misassignment.md` | `ticket-002` | Switching |
| Ticket-003 | `labs/helpdesk/ticket-003-proxmox-apt-egress-failure.md` | `ticket-003` | Linux |
| Ticket-004 | `labs/helpdesk/ticket-004-ssh-legacy-kex.md` | `ticket-004` | Security |
| Ticket-005 | `labs/helpdesk/ticket-005-vlan1-return-path-failure.md` | `ticket-005` | Networking |

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

## Deployment Steps on CT 120

Run from CT 120: `aria-ai-mentor-01`.

```bash
cd /opt/aria-ai-mentor/source/git-init-home-lab
git pull origin main

sudo cp services/ai-mentor/app/mentor_engine.py /opt/aria-ai-mentor/app/mentor_engine.py
sudo cp -r services/ai-mentor/lab_templates /opt/aria-ai-mentor/

sudo systemctl restart aria-ai-mentor
sudo systemctl status aria-ai-mentor --no-pager
```

Confirm service health:

```bash
curl -s http://127.0.0.1:8081/health | jq
```

Confirm KB status:

```bash
curl -s http://127.0.0.1:8081/kb/status | jq
```

Confirm template status using an authenticated browser session or admin token method if required:

```bash
curl -s http://127.0.0.1:8081/lab-templates/status | jq
```

---

## Validation Standard

Each ticket must pass these checks:

```text
[ ] Correct lab template is matched
[ ] Correct domain is returned in lab_template metadata
[ ] Mentor response includes template-aware guidance
[ ] Required evidence is shown
[ ] Missing evidence returns request_more_evidence
[ ] Complete evidence returns validation_complete
[ ] Retrieved sources include the related lab file and/or lab_template source
[ ] Student is coached without shortcut answers
[ ] Existing field-tech lab inventory remains untouched
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

Expected:

```text
lab_template.template_id = ticket-001
lab_template.domain = dns
next_action = request_more_evidence
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

Expected:

```text
next_action = validation_complete
```

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

Expected:

```text
lab_template.template_id = ticket-002
lab_template.domain = switching
next_action = validation_complete
```

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

Expected:

```text
lab_template.template_id = ticket-003
lab_template.domain = linux
next_action = validation_complete
```

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

Expected:

```text
lab_template.template_id = ticket-004
lab_template.domain = security
next_action = validation_complete
```

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

Expected:

```text
lab_template.template_id = ticket-005
lab_template.domain = networking
next_action = validation_complete
```

---

## Audit Validation

After the tests, inspect recent audit events:

```bash
curl -s http://127.0.0.1:8081/audit/recent?limit=20 | jq
```

Expected for authenticated/admin paths:

```text
mentor guidance events include lab_template_id and lab_template_domain where applicable
```

Note: unauthenticated `/mentor/analyze-ticket` calls may not create the same audit footprint as authenticated Zammad guidance routes.

---

## Phase 10 Completion Gate

Phase 10 can be marked complete only when:

```text
[ ] Ticket-001 missing-evidence and complete-evidence tests pass
[ ] Ticket-002 complete-evidence test passes
[ ] Ticket-003 complete-evidence test passes
[ ] Ticket-004 complete-evidence test passes
[ ] Ticket-005 complete-evidence test passes
[ ] Template metadata is returned for all five tickets
[ ] next_action behavior is acceptable
[ ] KB retrieval returns relevant lab context
[ ] No field-tech lab content was moved, overwritten, or reclassified
[ ] docs/aria-training-lab-inventory.md remains aligned with repo reality
```

---

## Next Phase After Completion

After Phase 10 is complete, proceed to:

```text
Phase 11 — Student-Facing Mentor Panel v1
```

Do not begin Phase 11 until Phase 10 validation evidence is captured.
