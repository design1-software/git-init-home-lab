# Monitoring Architecture

## Design Philosophy

This lab uses four distinct monitoring tiers. Each answers a different question and uses purpose-built tooling. There is no overlap between tiers.

| Question | Tier | Stack |
|---|---|---|
| Is the closet safe? | Environmental monitoring | closet-monitor (Streamlit) |
| Are the systems healthy? | Infrastructure monitoring | Prometheus + Grafana |
| Is something suspicious happening? | Security monitoring | Wazuh |
| What devices are present? | Network presence | NetAlertX |

This separation is deliberate. In enterprise environments, these are handled by separate teams with separate tools. A student who learns them as one undifferentiated "monitoring system" will be unprepared for real-world operations.

---

## Tier 1 — Environmental Monitoring

**Stack:** ESP32 · BME280 · MQTT → Mosquitto (Pi) → SQLite → Streamlit (Acer :8501)

**Answers:** Is the closet safe? Is the server environment within acceptable ranges?

**Metrics:** Temperature · Humidity · Pressure · RSSI · Sensor uptime

**Source:** [closet-monitor](https://github.com/design1-software/closet-monitor)

**Status:** Production ✅

**Why it stays separate from Grafana:** This is an IoT sensor application, not an infrastructure dashboard. The closet-monitor has its own data pipeline (MQTT → SQLite), its own anomaly detection (rolling z-scores), and its own presentation layer (Streamlit). Replacing it with a Prometheus exporter would add complexity without adding value — the sensor data model doesn't fit a pull-based scrape architecture, and the Streamlit dashboard is already purpose-built for the use case.

---

## Tier 2 — Infrastructure Monitoring

**Stack:** Prometheus · Grafana · snmp_exporter · node_exporter (ARIA VLAN 70)

**Answers:** Are the systems healthy? Is a switch port down? Is a device out of memory? Is PoE budget near its limit?

**Metrics:**
- Cisco C1111: CPU utilization · memory · interface throughput/errors · WAN uptime
- Cisco 3560CX: CPU utilization · memory · per-port traffic · PoE draw per port · OSPF neighbor state
- ARIA (Proxmox host): CPU · memory · disk I/O · NVMe health · network throughput
- Pi: CPU · memory · disk · temperature · NTP sync status
- Acer: CPU · memory · disk · Docker container health

**Deployment:**
- Prometheus LXC on ARIA VLAN 70
- Grafana LXC on ARIA VLAN 70 — access via `https://192.168.70.xx:3000`
- snmp_exporter on ARIA — polls C1111 and 3560CX via SNMPv2c
- node_exporter on ARIA, Pi, and Acer — scraped by Prometheus

**Cisco dashboard:** Grafana Labs community dashboard for snmp_exporter covers interface throughput, error rates, port status, CPU, and memory with near-zero custom configuration.

**Status:** Pending ARIA VLAN 70 cutover

**Why Grafana is not the closet dashboard:** Prometheus is a pull-based metrics system. It scrapes endpoints on a schedule. The closet-monitor uses a push-based MQTT model optimized for embedded sensor hardware. The data models, collection cadence, and operational questions are fundamentally different.

---

## Tier 3 — Security Monitoring

**Stack:** Wazuh SIEM (ARIA VLAN 70) + Wazuh agents (Acer, Pi, ARIA host)

**Answers:** Is something suspicious happening? Did a file change that shouldn't have? Are there brute-force attempts? Did a process run that shouldn't?

**Events:**
- SSH authentication failures and successes (rule 5763 — failures followed by success)
- File integrity violations on critical system files
- Suspicious process execution
- Log correlation across multiple hosts

**Dashboards:** Wazuh native dashboard (separate from Grafana — security events require SIEM-specific context and rule lookup)

**Status:** Pending ARIA VLAN 70 cutover

**Lab coverage:** See `labs/helpdesk/ticket-010-wazuh-alert-investigation.md`

---

## Tier 4 — Network Presence

**Stack:** NetAlertX (Pi — no ARIA dependency)

**Answers:** What devices are currently on the network? Is there a new or unknown device?

**Events:**
- New device detected (unknown MAC)
- Known device goes offline unexpectedly
- Device DHCP lease changes

**Status:** Pending deployment (can deploy now — Pi only, no ARIA dependency)

---

## Notification Layer

**Stack:** ntfy (Pi — self-hosted push notifications)

**Role:** Unified delivery channel for alerts from all four tiers.

| Source | ntfy Integration |
|---|---|
| closet-monitor | Anomaly detection alerts (temperature/humidity threshold breach) |
| Prometheus alertmanager | Infrastructure threshold alerts (port down, high CPU, PoE near limit) |
| Wazuh | Security event webhook → ntfy |
| NetAlertX | New device / unexpected offline alerts → ntfy |

**Status:** Pending deployment (can deploy now — Pi only)

**ntfy** is deployed on the Pi because it is lightweight and has no ARIA dependency. Alert routing from Prometheus and Wazuh will be configured after those services are deployed on ARIA.

---

## Deployment Order

| Step | Action | ARIA dependency |
|---|---|---|
| 1 | Deploy NetAlertX on Pi | No |
| 2 | Deploy ntfy on Pi | No |
| 3 | Deploy node_exporter on Pi and Acer | No |
| 4 | ARIA VLAN 70 cutover | — |
| 5 | Deploy Prometheus LXC on ARIA | Yes |
| 6 | Deploy Grafana LXC on ARIA | Yes |
| 7 | Configure snmp_exporter for C1111 + 3560CX | Yes |
| 8 | Deploy Wazuh LXC on ARIA | Yes |
| 9 | Install Wazuh agents on Acer, Pi, ARIA host | Yes |
| 10 | Wire ntfy as unified notification endpoint | Yes (Prometheus + Wazuh routing) |

---

## What This Teaches

| Tier | Enterprise Analogue |
|---|---|
| Environmental monitoring | BMS (Building Management System) sensor platforms |
| Infrastructure monitoring | Prometheus + Grafana is the de facto standard in cloud-native ops; SNMP dashboards are standard in network engineering |
| Security monitoring | SIEM platforms (Splunk, Microsoft Sentinel, Elastic SIEM) |
| Network presence | Network Access Control (NAC) and asset inventory tools |

A student who has operated all four tiers understands not just the tools, but why organizations run them separately — different data models, different audiences, different alert urgency, and different response procedures.

---

*Last updated: Jun 5, 2026*
