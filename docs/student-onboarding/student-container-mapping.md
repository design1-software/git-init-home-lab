# ARIA Student Account and Container Mapping

This document tracks the non-PII training identity mapping for ARIA students.

Do not store personal phone numbers, personal email addresses, or passwords in this repository.

## Current Students

| Student | AD Username | Domain UPN | Zammad Login | Linux Container | Proxmox CT | Linux User | Tailscale IP | Primary Training Track |
|---|---|---|---|---|---:|---|---|---|
| Sha Neal Prather | student01 | student01@jlm.lab | student01 | student-linux-01 | 102 | student01 | 100.76.81.39 | ARIA foundational labs |
| Dominique Davis | student02 | student02@jlm.lab | student02 | student-linux-02 | 103 | student02 | 100.91.190.9 | ARIA foundational labs |

## Validation Completed

### Sha Neal Prather

- Active Directory account exists.
- Account is assigned to the ARIA student identity path.
- Zammad account exists.
- Dedicated Linux container exists: `student-linux-01`.
- Tailscale identity is clean and mapped to `student-linux-01`.

### Dominique Davis

- Active Directory account exists.
- Account is assigned to the ARIA student identity path.
- Zammad account exists.
- Dedicated Linux container exists: `student-linux-02`.
- Linux user `student02` exists and has sudo access.
- SSH login to `student-linux-02` was validated.
- Tailscale identity is clean and mapped to `student-linux-02`.

## Final Student-to-Container Mapping

```text
Sha Neal Prather -> student01 -> student-linux-01 -> CT 102 -> 100.76.81.39
Dominique Davis  -> student02 -> student-linux-02 -> CT 103 -> 100.91.190.9
```

## Notes

- ARIA follows a one-student, one-container model for Linux practice.
- Student passwords must be provided out-of-band and should never be committed.
- Personal emails and phone numbers should remain in private onboarding records only.
