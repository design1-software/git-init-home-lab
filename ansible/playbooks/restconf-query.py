#!/usr/bin/env python3
"""
restconf-query.py
RESTCONF API queries against JLM-LAB-R1 (C1111, IOS XE 16.10)
Demonstrates REST API, HTTP methods, JSON parsing — CCNA Domain 6

Usage:
  CISCO_PASSWORD='password' python3 restconf-query.py

Requirements:
  pip install requests
"""

import os
import sys
import json
import requests
from requests.auth import HTTPBasicAuth

# Suppress self-signed cert warnings
requests.packages.urllib3.disable_warnings()

# ============================================================
# Connection settings
# ============================================================
HOST = "192.168.10.1"
USERNAME = os.environ.get("CISCO_USERNAME", "admin")
PASSWORD = os.environ.get("CISCO_PASSWORD")
BASE_URL = f"https://{HOST}/restconf/data"
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}


def restconf_get(path: str) -> dict:
    """Make a RESTCONF GET request and return parsed JSON."""
    url = f"{BASE_URL}/{path}"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        headers=HEADERS,
        verify=False
    )
    response.raise_for_status()
    return response.json()


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def main():
    if not PASSWORD:
        print("ERROR: CISCO_PASSWORD environment variable not set.")
        print("Usage: CISCO_PASSWORD='password' python3 restconf-query.py")
        sys.exit(1)

    print(f"RESTCONF API Queries — {HOST}")
    print(f"User: {USERNAME}")

    # --------------------------------------------------------
    # Query 1: Hostname
    # --------------------------------------------------------
    print_section("Query 1: Device Hostname")
    data = restconf_get("Cisco-IOS-XE-native:native/hostname")
    hostname = data.get("Cisco-IOS-XE-native:hostname")
    print(f"Hostname: {hostname}")

    # --------------------------------------------------------
    # Query 2: IOS Version
    # --------------------------------------------------------
    print_section("Query 2: IOS Version")
    data = restconf_get("Cisco-IOS-XE-native:native/version")
    version = data.get("Cisco-IOS-XE-native:version")
    print(f"IOS XE Version: {version}")

    # --------------------------------------------------------
    # Query 3: Interface summary
    # --------------------------------------------------------
    print_section("Query 3: Interface Summary")
    data = restconf_get("Cisco-IOS-XE-native:native/interface")
    interfaces = data.get("Cisco-IOS-XE-native:interface", {})
    gi_interfaces = interfaces.get("GigabitEthernet", [])

    print(f"{'Interface':<20} {'Status':<15} {'VLAN/IP'}")
    print(f"{'-'*20} {'-'*15} {'-'*20}")

    for intf in gi_interfaces:
        name = f"GigabitEthernet{intf['name']}"
        status = "shutdown" if "shutdown" in intf else "enabled"

        # Determine VLAN or IP
        detail = ""
        if "switchport" in intf:
            sw = intf["switchport"]
            access = sw.get("Cisco-IOS-XE-switch:access", {})
            trunk = sw.get("Cisco-IOS-XE-switch:trunk", {})
            if access:
                vlan = access.get("vlan", {}).get("vlan", "")
                detail = f"access VLAN {vlan}"
            elif trunk:
                native = trunk.get("native", {}).get("vlan", "")
                detail = f"trunk native {native}"
        elif "ip" in intf:
            ip = intf["ip"]
            if "address" in ip:
                addr = ip["address"]
                if "dhcp" in addr:
                    detail = "DHCP"
                elif "primary" in addr:
                    primary = addr["primary"]
                    detail = f"{primary.get('address')}/{primary.get('mask')}"

        print(f"{name:<20} {status:<15} {detail}")

    # --------------------------------------------------------
    # Query 4: OSPF configuration
    # --------------------------------------------------------
    print_section("Query 4: OSPF Configuration")
    try:
        data = restconf_get(
            "Cisco-IOS-XE-native:native/router"
            "/Cisco-IOS-XE-ospf:ospf"
        )
        ospf_list = data.get("Cisco-IOS-XE-ospf:ospf", [])
        for process in ospf_list:
            pid = process.get("id")
            router_id = process.get(
                "Cisco-IOS-XE-ospf:router-id", "not set"
            )
            networks = process.get("network", [])
            print(f"OSPF Process: {pid}")
            print(f"Router ID:    {router_id}")
            print(f"Networks:     {len(networks)} configured")
            for net in networks:
                ip = net.get("ip")
                mask = net.get("mask")
                area = net.get("area")
                print(f"              {ip} {mask} area {area}")
    except requests.exceptions.HTTPError as e:
        print(f"OSPF query returned: {e.response.status_code} — "
              f"may not be in this YANG path")

    # --------------------------------------------------------
    # Query 5: NTP configuration
    # --------------------------------------------------------
    print_section("Query 5: NTP Servers")
    try:
        data = restconf_get(
            "Cisco-IOS-XE-native:native/ntp"
        )
        ntp = data.get("Cisco-IOS-XE-native:ntp", {})
        servers = ntp.get(
            "Cisco-IOS-XE-ntp:server", {}
        ).get("server-list", [])
        for s in servers:
            print(f"NTP Server: {s.get('ip-address')}")
        master = ntp.get("Cisco-IOS-XE-ntp:master", {})
        if master:
            print(f"NTP Master: stratum {master.get('stratum', 'configured')}")
    except Exception as e:
        print(f"NTP query: {e}")

    print(f"\n{'='*60}")
    print("  RESTCONF queries complete")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
