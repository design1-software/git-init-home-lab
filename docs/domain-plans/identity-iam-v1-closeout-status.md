# Identity / IAM v1 Closeout Status

## Status

Identity / IAM / Active Directory / GPO / Windows Endpoint Administration is now network-ready and scaffold-complete for v1.

The instructional workflow, evidence templates, VLAN 60 workload path, and training asset management boundary are in place.

Full AD/GPO infrastructure completion is still pending Windows Server and Windows client deployment.

## Completed

- Identity/IAM domain plan created
- VLAN 60 scope corrected from build to validate
- Training asset management boundary documented
- VLAN 60 switch-side validation completed
- Proxmox VLAN 60 workload path completed using dedicated vmbr1/nic0/Gi0/6 access VLAN 60 design
- VLAN 70 Proxmox management path preserved on vmbr0/nic1/Gi0/4
- Identity/IAM lab submission templates created
- Runtime templates copied into the AI Mentor template directory
- AI Mentor service restarted successfully
- Health check passed
- Identity/IAM scaffold committed to GitHub

## Phase D VLAN 60 End-to-End Path

Phase D VLAN 60 is now proven end-to-end.

Validated path:

LXC container on vmbr1
  -> untagged frames
nic0 10:ff:e0:c4:fa:a6
  -> Cat6
3560CX Gi0/6 access VLAN 60
  -> Vlan60 SVI 192.168.60.1
  -> LAB-ACL inbound
  -> DHCP snooping + DAI + IP Source Guard
  -> 3560CX OSPF area 0
  -> 192.168.199.0/30 transit
  -> C1111 OSPF + NAT inside for 192.168.60.0/24
  -> GigabitEthernet0/0/0
  -> WAN 174.53.28.46
  -> Internet

## Network Separation

The final safe design separates management and lab workloads.

### VLAN 70 Management Path

Proxmox host management
  -> vmbr0
  -> nic1
  -> 3560CX Gi0/4 access VLAN 70
  -> VLAN 70 SERVER

VLAN 70 remains the stable management path for:

- Proxmox host access
- ARIA AI Mentor CT
- Zammad CT
- Existing server-side infrastructure
- Administrative access

### VLAN 60 Lab Workload Path

AD/IAM lab workload
  -> vmbr1
  -> nic0
  -> 3560CX Gi0/6 access VLAN 60
  -> VLAN 60 LAB

VLAN 60 is now ready for:

- JLM-DC01
- JLM-WIN01
- AD/GPO/IAM labs
- Training-only Windows clients
- Training-only Windows servers
- Training asset management exercises

Because Gi0/6 is an access VLAN 60 port, VMs and containers attached to vmbr1 should use untagged network interfaces unless Gi0/6 is redesigned as a trunk later.

## VLAN 60 Switch-Side Validation

Validated on JLM-LAB-SW1:

- VLAN 60 exists and is active
- Vlan60 SVI is up/up
- Gateway is 192.168.60.1/24
- LAB-ACL is applied inbound on Vlan60
- LAB DHCP pool exists
- DHCP gateway is 192.168.60.1
- DHCP DNS is 192.168.10.16 and 1.1.1.1
- DHCP snooping is active
- Dynamic ARP Inspection is active
- IP Source Guard is active on the access path
- OSPF area 0 carries VLAN 60 routing
- C1111 NAT inside includes 192.168.60.0/24
- Internet access from VLAN 60 is validated

## Identity/IAM Runtime Templates

The following templates were created:

- identity-iam-ad-user-lifecycle-v1
- identity-iam-ad-group-access-v1
- identity-iam-domain-join-v1
- identity-iam-gpo-validation-v1
- identity-iam-training-asset-management-v1

## Training Asset Management Boundary

The VLAN 60 jlm.lab training domain may manage training assets only.

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

## Remaining AD/GPO Deployment Tasks

Identity/IAM is now ready for AD deployment, but full infrastructure completion still requires:

- Upload Windows Server ISO
- Upload Windows client ISO
- Create JLM-DC01 VM on vmbr1
- Assign static VLAN 60 IP to JLM-DC01
- Install AD DS and DNS
- Promote JLM-DC01 as the first domain controller for jlm.lab
- Create OU structure
- Create initial users and groups
- Create JLM-WIN01 VM on vmbr1
- Point JLM-WIN01 DNS to JLM-DC01
- Join JLM-WIN01 to jlm.lab
- Test ADUC, DNS, GPO, gpresult, rsop.msc, Event Viewer, password reset, group membership, domain join, and user lifecycle workflows
- Rebuild KB after final documentation commit

## Closeout Assessment

Identity/IAM v1 is now network-ready and scaffold-complete.

The previous blocker, Proxmox VLAN 60 workload access, is resolved by the dedicated vmbr1/nic0/Gi0/6 access VLAN 60 path.

The domain should not be marked fully AD/GPO infrastructure-complete until JLM-DC01 and JLM-WIN01 are deployed and tested.
