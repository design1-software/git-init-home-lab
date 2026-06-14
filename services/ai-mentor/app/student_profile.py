from typing import Any, Dict


STUDENT_PROFILES: Dict[str, Dict[str, Any]] = {
    "student01": {
        "display_name": "Sha Neal Prather",
        "zammad_login": "student01",
        "linux_host": "student-linux-01",
        "linux_ssh": "ssh student01@100.76.81.39",
        "target_systems": [
            {
                "name": "student-linux-01",
                "type": "linux_container",
                "access": "ssh student01@100.76.81.39",
                "purpose": "Linux command-line labs and evidence collection",
            }
        ],
    },
    "student02": {
        "display_name": "Dominique Davis",
        "zammad_login": "student02",
        "linux_host": "student-linux-02",
        "linux_ssh": "ssh student02@100.91.190.9",
        "target_systems": [
            {
                "name": "student-linux-02",
                "type": "linux_container",
                "access": "ssh student02@100.91.190.9",
                "purpose": "Linux command-line labs and evidence collection",
            }
        ],
    },
}


DEFAULT_WORKFLOW_SYSTEMS = [
    {
        "name": "Zammad",
        "purpose": "Read the assigned ticket and write the final ticket note.",
    },
    {
        "name": "ARIA AI Mentor",
        "purpose": "Load the ticket, request evidence guidance, validate evidence, and draft the final note.",
    },
    {
        "name": "Lab Target System",
        "purpose": "Run the actual troubleshooting commands and collect real evidence.",
    },
]


def get_student_profile(username: str) -> Dict[str, Any]:
    normalized = str(username or "").strip()
    profile = STUDENT_PROFILES.get(normalized, {})

    return {
        "username": normalized,
        "display_name": profile.get("display_name", normalized),
        "zammad_login": profile.get("zammad_login", normalized),
        "linux_host": profile.get("linux_host", ""),
        "linux_ssh": profile.get("linux_ssh", ""),
        "target_systems": profile.get("target_systems", []),
        "workflow_systems": DEFAULT_WORKFLOW_SYSTEMS,
    }
