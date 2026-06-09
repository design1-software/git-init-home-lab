from typing import Any, Dict, List, Tuple
import re

from app.models import AnalyzeTicketRequest


COMPLETION_PHRASES = [
    "resolution summary",
    "zammad v1 platform validation passed",
    "ticket-009 confirms the basic training-ticket workflow",
]


TICKET_WORKFLOWS: Dict[str, Dict[str, Any]] = {
    "001": {
        "title": "DNS Resolution Failing",
        "domain": "DNS / Pi-hole",
        "situation": "The student is troubleshooting a client that has network connectivity but cannot resolve names.",
        "evidence_checks": [
            {
                "id": "ip_connectivity",
                "label": "IP connectivity test",
                "keywords": ["ping 8.8.8.8", "gateway", "ip connectivity", "icmp", "reachable by ip"],
                "prompt": "Provide proof that the client can or cannot reach a destination by IP address.",
            },
            {
                "id": "dns_query_result",
                "label": "DNS query result",
                "keywords": ["nslookup", "dig", "ping google.com", "name resolution", "dns query", "resolve"],
                "prompt": "Provide nslookup, dig, or equivalent DNS query output from the affected client.",
            },
            {
                "id": "client_dns_config",
                "label": "Client DNS configuration",
                "keywords": ["dns server", "ipconfig", "resolvectl", "networksetup", "resolv.conf", "192.168.10.16"],
                "prompt": "Show which DNS server the client is actually configured to use.",
            },
        ],
        "documentation_prompt": "Write the incident summary showing symptom, tests used to isolate DNS, root cause, action taken, and final nslookup verification.",
    },
    "002": {
        "title": "Device on Wrong VLAN",
        "domain": "VLAN / Switching / DHCP",
        "situation": "The student is verifying whether an endpoint landed on the wrong VLAN or received the wrong DHCP scope.",
        "evidence_checks": [
            {
                "id": "switchport_status",
                "label": "Switchport or SSID status",
                "keywords": ["show interfaces status", "switchport", "port", "ssid", "gorgeous-iot", "ap port"],
                "prompt": "Identify the switchport, AP port, or SSID path associated with the affected device.",
            },
            {
                "id": "assigned_vlan",
                "label": "Assigned VLAN or observed subnet",
                "keywords": ["192.168.100", "vlan 1", "vlan1", "access vlan", "assigned vlan", "pvid"],
                "prompt": "Show the VLAN or subnet the device is currently using.",
            },
            {
                "id": "expected_vlan",
                "label": "Expected VLAN",
                "keywords": ["192.168.30", "vlan 30", "iot", "expected vlan", "correct vlan"],
                "prompt": "State the expected VLAN or subnet and compare it against the observed address.",
            },
        ],
        "documentation_prompt": "Write the incident summary showing observed IP, expected VLAN, misconfiguration location, correction, and DHCP verification after reconnect.",
    },
    "003": {
        "title": "Proxmox Host Cannot Run apt update",
        "domain": "Linux / Proxmox / Package Management",
        "situation": "The student is separating package repository failure from DNS, routing, and outbound egress failure.",
        "evidence_checks": [
            {
                "id": "apt_error",
                "label": "APT error output",
                "keywords": ["apt update", "network is unreachable", "temporary failure resolving", "401", "404", "enterprise.proxmox", "pve-no-subscription"],
                "prompt": "Provide the exact apt update error output before changing repository files.",
            },
            {
                "id": "dns_test",
                "label": "DNS test",
                "keywords": ["download.proxmox.com", "nslookup", "dig", "temporary failure resolving", "resolve"],
                "prompt": "Test name resolution for the repository host from the affected Proxmox system.",
            },
            {
                "id": "gateway_test",
                "label": "Gateway or internet reachability test",
                "keywords": ["ping -c 3 8.8.8.8", "ping 8.8.8.8", "gateway", "ip route", "internet reachability"],
                "prompt": "Show whether the host can reach its gateway or an external IP.",
            },
        ],
        "documentation_prompt": "Write the incident summary showing the apt symptom, network checks, repository/source findings, changes made, and final apt update result.",
    },
    "004": {
        "title": "Cannot SSH Into Switch — Legacy Key Exchange",
        "domain": "Cisco / SSH / Security",
        "situation": "The student is distinguishing a reachable device with SSH negotiation failure from basic network downtime.",
        "evidence_checks": [
            {
                "id": "ssh_error",
                "label": "SSH error message",
                "keywords": ["no matching key exchange", "unable to negotiate", "host key", "ssh-rsa", "diffie-hellman", "kex"],
                "prompt": "Provide the exact SSH error message instead of summarizing it.",
            },
            {
                "id": "ssh_verbose_output",
                "label": "Verbose SSH output",
                "keywords": ["ssh -v", "debug1", "kexalgorithms", "hostkeyalgorithms", "their offer"],
                "prompt": "Provide safe verbose SSH output showing where negotiation fails.",
            },
            {
                "id": "risk_statement",
                "label": "Security risk statement",
                "keywords": ["legacy", "temporary", "security risk", "weaken", "upgrade", "long-term remediation", "controlled lab"],
                "prompt": "Acknowledge that legacy algorithms are a temporary compatibility workaround, not a permanent security posture.",
            },
        ],
        "documentation_prompt": "Write the incident summary showing device, SSH error type, evidence from verbose output, temporary compatibility path, and long-term remediation note.",
    },
    "005": {
        "title": "VLAN 1 Return Path Failure",
        "domain": "Routing / NAT / Transitional Network Architecture",
        "situation": "The student is proving a return-path or asymmetric-routing failure rather than assuming a simple internet outage.",
        "evidence_checks": [
            {
                "id": "source_destination",
                "label": "Source and destination",
                "keywords": ["192.168.100.10", "8.8.8.8", "source", "destination", "aria", "vlan 1"],
                "prompt": "Identify the source, destination, and expected path for the failed test.",
            },
            {
                "id": "forward_path",
                "label": "Forward path evidence",
                "keywords": ["ping -c 3 192.168.100.1", "gateway", "nslookup", "ip route get", "forward path", "default route"],
                "prompt": "Show whether traffic leaves the source network and which route is selected.",
            },
            {
                "id": "return_path",
                "label": "Return path evidence",
                "keywords": ["return path", "asymmetric", "show ip route 192.168.100.0", "show ip nat translations", "source vlan 1", "vlan1 svi", "arp fails"],
                "prompt": "Provide evidence that replies are or are not returning through the expected VLAN path.",
            },
        ],
        "documentation_prompt": "Write the structured incident summary showing forward-path checks, return-path proof, why the fix is temporary, and what prevents recurrence after cleanup.",
    },

    "006": {
        "title": "Proxmox Repository Hygiene",
        "domain": "Proxmox / Linux / Package Management",
        "situation": "The student is validating Proxmox repository configuration and confirming apt update works without enterprise repository errors.",
        "evidence_checks": [
            {
                "id": "apt_update_error",
                "label": "APT update error",
                "keywords": ["apt update", "pve-enterprise", "enterprise.proxmox", "no subscription", "repository error", "401", "403", "apt error"],
                "prompt": "Provide the apt update output or repository-related error before making changes.",
            },
            {
                "id": "repo_files",
                "label": "Repository source files",
                "keywords": ["sources.list", "pve-enterprise.list", "debian.sources", "apt sources", "/etc/apt", "pve-no-subscription", "download.proxmox.com"],
                "prompt": "Identify the relevant apt source files and show which repository entries are enabled or disabled.",
            },
            {
                "id": "successful_update",
                "label": "Successful apt update",
                "keywords": ["apt update completes", "reading package lists", "all packages are up to date", "hit:", "get:", "fetched", "successful apt update", "no enterprise repository error"],
                "prompt": "Confirm apt update works after the repository correction.",
            },
        ],
        "documentation_prompt": "Write the incident summary showing the original apt symptom, repository files reviewed, correction made, and final successful apt update result.",
    },
    "007": {
        "title": "Proxmox VLAN 70 Migration",
        "domain": "Proxmox / VLAN / Migration Validation",
        "situation": "The student is validating that an ARIA service or host was moved to VLAN 70 and remains reachable after migration.",
        "evidence_checks": [
            {
                "id": "ip_addressing",
                "label": "VLAN 70 IP addressing",
                "keywords": ["192.168.70", "vlan 70", "vlan70", "ip -br addr", "ip addr", "vmbr0", "addressing", "expected ip", "actual ip"],
                "prompt": "Document the expected and actual VLAN 70 IP configuration.",
            },
            {
                "id": "gateway_reachability",
                "label": "Gateway reachability",
                "keywords": ["192.168.70.1", "gateway", "ping -c", "ping 192.168.70.1", "default route", "ip route"],
                "prompt": "Confirm the system can reach the VLAN 70 gateway and show the routing evidence.",
            },
            {
                "id": "service_reachability",
                "label": "Service reachability",
                "keywords": ["curl", "http", "service", "port", "8081", "zammad", "aria", "reachable", "health", "access validated"],
                "prompt": "Confirm the ARIA service is reachable after migration.",
            },
        ],
        "documentation_prompt": "Write the change-validation summary showing VLAN 70 addressing, gateway reachability, service reachability, and rollback considerations.",
    },
    "008": {
        "title": "Comet ATX Hard Reset Validation",
        "domain": "Hardware Ops / Power Control / Recovery Validation",
        "situation": "The student is validating a controlled ATX hard reset or power-control action and confirming system recovery afterward.",
        "evidence_checks": [
            {
                "id": "precheck",
                "label": "Pre-reset check",
                "keywords": ["precheck", "pre-reset", "before reset", "before power cycle", "system state", "status before", "baseline"],
                "prompt": "Document the system state before performing the reset.",
            },
            {
                "id": "reset_action",
                "label": "Reset action evidence",
                "keywords": ["hard reset", "power cycle", "atx", "reset action", "power control", "comet", "reboot initiated", "power reset"],
                "prompt": "Document the ATX reset or power-control action performed.",
            },
            {
                "id": "postcheck",
                "label": "Post-reset recovery check",
                "keywords": ["postcheck", "post-reset", "after reset", "recovered", "booted", "online", "service restored", "ping succeeds", "health check"],
                "prompt": "Confirm the system recovered after reset and provide recovery evidence.",
            },
        ],
        "documentation_prompt": "Write the validation summary showing pre-reset state, reset action, post-reset recovery, and any safety notes.",
    },
    "010": {
        "title": "Wazuh Alert Investigation",
        "domain": "Security Monitoring / SOC / Alert Triage",
        "situation": "The student is investigating a Wazuh security alert and documenting alert details, affected asset, disposition, and next step.",
        "evidence_checks": [
            {
                "id": "alert_details",
                "label": "Alert details",
                "keywords": ["wazuh", "rule id", "severity", "timestamp", "alert title", "alert details", "agent", "siem"],
                "prompt": "Provide the alert title, rule ID, severity, timestamp, and source system.",
            },
            {
                "id": "affected_asset",
                "label": "Affected asset",
                "keywords": ["affected asset", "endpoint", "host", "agent", "user", "service", "asset", "source ip", "hostname"],
                "prompt": "Identify the affected endpoint, user, service, or host.",
            },
            {
                "id": "disposition",
                "label": "Disposition",
                "keywords": ["benign", "suspicious", "escalate", "escalation", "false positive", "true positive", "requires escalation", "reasoning", "next step"],
                "prompt": "Classify the alert as benign, suspicious, or requiring escalation, and explain why.",
            },
        ],
        "documentation_prompt": "Write the security triage summary showing alert details, affected asset, disposition, reasoning, and whether escalation is required.",
    },

}


def normalize_for_detection(text: str) -> str:
    normalized = text.lower()
    normalized = re.sub(r"<[^>]+>", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def ticket_009_is_complete(text: str) -> bool:
    normalized = normalize_for_detection(text)
    return all(phrase in normalized for phrase in COMPLETION_PHRASES)


def format_sources(kb_results: List[Dict[str, Any]]) -> str:
    if not kb_results:
        return "No KB source was retrieved for this request."

    lines = []
    for index, item in enumerate(kb_results[:3], start=1):
        lines.append(
            f"{index}. {item.get('source_path')} "
            f"(category: {item.get('category')}, chunk: {item.get('chunk_index')}, score: {item.get('score')})"
        )
    return "\n".join(lines)


def unique_sources(kb_results: List[Dict[str, Any]]) -> List[str]:
    sources = []
    for item in kb_results:
        source = item.get("source_path")
        if source and source not in sources:
            sources.append(source)
    return sources


def normalize_ticket_id(ticket_id: str, title: str = "", body: str = "") -> str:
    combined = f"{ticket_id} {title} {body}".lower()

    explicit_match = re.search(r"ticket[-\s_]*(\d{1,3})", combined)
    if explicit_match:
        return explicit_match.group(1).zfill(3)

    numeric_match = re.fullmatch(r"\d{1,3}", str(ticket_id).strip())
    if numeric_match:
        return numeric_match.group(0).zfill(3)

    title_map = {
        "dns": "001",
        "vlan misassignment": "002",
        "wrong vlan": "002",
        "apt": "003",
        "proxmox host cannot run apt": "003",
        "ssh legacy": "004",
        "legacy key exchange": "004",
        "return path": "005",
        "asymmetric routing": "005",
        "repo hygiene": "006",
        "enterprise repository": "006",
        "pve-enterprise": "006",
        "vlan 70 migration": "007",
        "vlan70": "007",
        "comet": "008",
        "hard reset": "008",
        "atx": "008",
        "wazuh": "010",
        "alert investigation": "010",
        "security alert": "010",
        "zammad ticket triage": "009",
    }

    for marker, mapped_id in title_map.items():
        if marker in combined:
            return mapped_id

    return str(ticket_id).strip().zfill(3)


def evaluate_evidence(evidence_text: str, checks: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    normalized = normalize_for_detection(evidence_text)
    present: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []

    for check in checks:
        keywords = [str(keyword).lower() for keyword in check.get("keywords", [])]
        if any(keyword in normalized for keyword in keywords):
            present.append(check)
        else:
            missing.append(check)

    return present, missing


def format_evidence_list(items: List[Dict[str, Any]], empty_message: str) -> str:
    if not items:
        return empty_message

    return "\n".join(f"{index}. {item.get('label')}" for index, item in enumerate(items, start=1))


def format_missing_prompts(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "No missing evidence detected."

    return "\n".join(
        f"{index}. {item.get('label')}: {item.get('prompt')}"
        for index, item in enumerate(items, start=1)
    )


def build_ticket_workflow_response(
    ticket_id: str,
    workflow: Dict[str, Any],
    request: AnalyzeTicketRequest,
    kb_results: List[Dict[str, Any]],
) -> Tuple[str, str, str, List[str]]:
    evidence = (request.student_evidence or "").strip()
    ticket_text = f"{request.ticket_title}\n{request.ticket_body}\n{evidence}".strip()
    sources_text = format_sources(kb_results)
    retrieved_sources = unique_sources(kb_results)

    default_source = f"labs/helpdesk/ticket-{ticket_id}-{workflow['title'].lower().replace(' ', '-').replace('—', '').replace('/', '-')}.md"
    if not retrieved_sources:
        retrieved_sources = [default_source]

    present, missing = evaluate_evidence(ticket_text, workflow["evidence_checks"])

    if not evidence:
        next_action = "request_more_evidence"
        assessment = "No student evidence has been provided yet. ARIA should coach the student through evidence collection before any fix is confirmed."
    elif missing:
        next_action = "request_more_evidence"
        assessment = "Some evidence is present, but the workflow is not ready for completion because required evidence is still missing."
    else:
        next_action = "validation_complete"
        assessment = "The submitted evidence appears to cover the required validation points. Instructor review can verify the work and capture the portfolio-ready summary."

    mentor_response = f"""--- ARIA Mentor ---

Situation Summary:
Ticket-{ticket_id} is mapped to the {workflow['title']} workflow.
{workflow['situation']}

Source Context Used:
{sources_text}

Assessment:
{assessment}

Evidence Detected:
{format_evidence_list(present, 'No required evidence detected yet.')}

Evidence Still Needed:
{format_missing_prompts(missing)}

Coaching Direction:
1. Do not jump straight to a fix.
2. Prove the issue domain with command output or observed system state.
3. Compare the observed state against the expected state.
4. Document what changed and how the fix was verified.

Documentation Standard:
{workflow['documentation_prompt']}

Next Step:
{next_action}

--- End ---"""

    return mentor_response, "low", next_action, retrieved_sources


def build_ticket_009_completion_response(
    request: AnalyzeTicketRequest,
    kb_results: List[Dict[str, Any]],
) -> Tuple[str, str, str, List[str]]:
    sources_text = format_sources(kb_results)
    retrieved_sources = unique_sources(kb_results)

    if not retrieved_sources:
        retrieved_sources = ["labs/helpdesk/ticket-009-zammad-ticket-triage.md"]

    mentor_response = f"""--- ARIA Mentor ---

Situation Summary:
Ticket-009 appears complete.

Source Context Used:
{sources_text}

Validation Observed:
1. Student accessed the ticket.
2. Student added an update.
3. Resolution summary is present.
4. Ticket workflow validation was documented.

Next Step:
Instructor can mark this lab as complete and capture the portfolio output.

--- End ---"""
    return mentor_response, "low", "validation_complete", retrieved_sources


def build_ticket_009_response(
    request: AnalyzeTicketRequest,
    kb_results: List[Dict[str, Any]],
) -> Tuple[str, str, str, List[str]]:
    evidence = (request.student_evidence or "").strip()
    sources_text = format_sources(kb_results)
    retrieved_sources = unique_sources(kb_results)

    if not retrieved_sources:
        retrieved_sources = ["labs/helpdesk/ticket-009-zammad-ticket-triage.md"]

    combined_ticket_text = f"{request.ticket_title}\n{request.ticket_body}\n{evidence}"

    if ticket_009_is_complete(combined_ticket_text):
        return build_ticket_009_completion_response(request, kb_results)

    if not evidence:
        mentor_response = f"""--- ARIA Mentor ---

Situation Summary:
You are working on Ticket-{request.ticket_id}, a basic ARIA Help Desk ticket workflow validation.

Source Context Used:
{sources_text}

What I need to see:
1. Confirm that you can open the ticket.
2. Add a comment describing what the ticket is asking you to do.
3. Add one sentence explaining what evidence proves the workflow is working.

Why this matters:
In real help desk work, the ticket is the operational record. A useful ticket update helps the next technician, the instructor, and the customer understand what happened.

Evidence Standard:
Do not just write "done." A professional ticket update should describe what you saw, what you did, and what the result was.

Next Step:
Post a short professional update in the ticket, then provide that update as evidence.

--- End ---"""
        return mentor_response, "low", "student_update_required", retrieved_sources

    mentor_response = f"""--- ARIA Mentor ---

Situation Summary:
You provided evidence for Ticket-{request.ticket_id}: {evidence}

Source Context Used:
{sources_text}

Assessment:
This evidence is appropriate for a beginner help desk workflow validation if it confirms ticket access, ticket visibility, commenting, and update history.

What I need to see next:
1. Confirm whether the instructor/admin can see your comment.
2. Confirm whether the ticket can be closed with a clear resolution summary.
3. Write one professional closure sentence.

Suggested Closure Language:
"Zammad ticket workflow validated. I was able to access the ticket, review the request, add a comment, and confirm the ticket history captured the update."

Why this matters:
A ticket is not complete just because the task was performed. It is complete when the work is documented clearly enough for another person to understand what happened.

Next Step:
Add the closure summary and ask the instructor to verify and close the ticket.

--- End ---"""
    return mentor_response, "low", "closure_summary_required", retrieved_sources


def analyze_ticket(
    request: AnalyzeTicketRequest,
    kb_results: List[Dict[str, Any]] | None = None,
) -> Tuple[str, str, str, List[str]]:
    kb_results = kb_results or []
    normalized_title = request.ticket_title.lower()
    normalized_ticket_id = normalize_ticket_id(request.ticket_id, request.ticket_title, request.ticket_body)

    if normalized_ticket_id in TICKET_WORKFLOWS:
        return build_ticket_workflow_response(
            ticket_id=normalized_ticket_id,
            workflow=TICKET_WORKFLOWS[normalized_ticket_id],
            request=request,
            kb_results=kb_results,
        )

    if normalized_ticket_id == "009" or request.ticket_id in {"009", "4"} or "zammad ticket triage" in normalized_title:
        return build_ticket_009_response(request, kb_results)

    sources_text = format_sources(kb_results)
    retrieved_sources = unique_sources(kb_results)

    mentor_response = f"""--- ARIA Mentor ---

Situation Summary:
This ticket type is not fully mapped yet.

Source Context Used:
{sources_text}

What I need to see:
1. State the issue in one sentence.
2. Provide the exact evidence you have.
3. Explain what you think the next step should be.

Why this matters:
ARIA Mentor requires evidence before diagnosis. Do not jump to a fix without confirming what is actually happening.

Next Step:
Add ticket evidence and classify the issue domain.

--- End ---"""
    return mentor_response, "low", "evidence_required", retrieved_sources
