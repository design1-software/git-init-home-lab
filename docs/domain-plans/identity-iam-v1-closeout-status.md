# Identity / IAM v1 Closeout Status

## Status

Identity / IAM / Active Directory / GPO / Windows Endpoint Administration is partially completed for v1.

The instructional workflow, evidence templates, and domain plan are now in place. Physical AD deployment remains pending because the Proxmox VLAN 60 workload path needs a safer design window.

## Completed

- Identity/IAM domain plan created
- VLAN 60 scope corrected from "build" to "validate"
- Training asset management boundary documented
- VLAN 60 switch-side validation completed
- Identity/IAM lab submission templates created
- Runtime templates copied into the AI Mentor template directory
- AI Mentor service restarted successfully
- Health check passed

## VLAN 60 Switch-Side Validation

Validated on JLM-LAB-SW1:

- VLAN 60 exists and is active
- Vlan60 SVI is up/up
- Gateway is 192.168.60.1/24
- LAB-ACL is applied inbound on Vlan60
- LAB DHCP pool exists
- DHCP gateway is 192.168.60.1
- DHCP DNS is 192.168.10.16 and 1.1.1.1
- Gi0/2 trunk to GS308EP allows VLAN 60
- Gi0/2 forwards VLAN 60 in STP
- 192.168.60.0/24 is directly connected
- No active VLAN 60 DHCP leases were present before workloads

## Proxmox VLAN 60 Status

Proxmox remains stable on VLAN 70:

- Proxmox host: 192.168.70.10/24
- Gateway reachability to 192.168.70.1 passed
- Pi-hole reachability to 192.168.10.16 passed
- Internet reachability to 1.1.1.1 passed
- vmbr0 restored to simple access VLAN 70 behavior

The attempted trunk conversion was rolled back safely.

Current blocker:

- Gi0/4 is restored as access VLAN 70.
- vmbr0 is not carrying VLAN 60 workloads yet.
- Comet KVM HDMI is not reliable enough to continue risky uplink changes under time pressure.
- A safer maintenance window is required before converting the Proxmox uplink to trunk/native VLAN 70 with tagged VLAN 60 workload support.

## Identity/IAM Runtime Templates

The following templates were created:

- identity-iam-ad-user-lifecycle-v1
- identity-iam-ad-group-access-v1
- identity-iam-domain-join-v1
- identity-iam-gpo-validation-v1
- identity-iam-training-asset-management-v1

## Training Asset Management Boundary

The VLAN 60 `jlm.lab` training domain may manage training assets only.

Allowed training assets include:

- Domain-joined Windows training clients
- Training-only Windows servers
- Training file shares
- Training printer objects
- Training application server objects
- Simulated department workstations
- Lab computer objects
- Lab OUs
- Lab security groups
- Lab GPO scopes
- Lab onboarding/offboarding workflows

The training domain must not manage real production infrastructure in v1, including:

- Real Cisco C1111 router
- Real Catalyst 3560CX switch
- Real Proxmox host management plane
- Real Pi-hole DNS service
- Real UniFi controller
- Real CUPS/printing service
- Real household, guest, IoT, or MGMT assets
- Real credentials or secrets used to administer the home lab

## Pending

- Upload Windows Server ISO
- Upload Windows client ISO
- Create safe Proxmox VLAN 60 workload path
- Deploy JLM-DC01 on VLAN 60
- Deploy JLM-WIN01 on VLAN 60
- Join JLM-WIN01 to jlm.lab
- Test ADUC, DNS, GPO, gpresult, rsop.msc, and Event Viewer workflows
- Create IAM ticket workflows after the AD lab exists
- Rebuild KB after documentation commit

## Closeout Assessment

Identity/IAM is not fully infrastructure-complete yet because the AD VM and Windows client are not deployed.

However, Identity/IAM now has the required v1 planning, safety boundary, VLAN validation, evidence templates, and mentor scaffolding needed to proceed once the Proxmox VLAN 60 workload path is safely implemented.

