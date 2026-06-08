import argparse
import getpass
import sys
from pathlib import Path

ROOT = Path("/opt/aria-ai-mentor")
sys.path.insert(0, str(ROOT))

from app.auth import SUPPORTED_ROLES, find_user, hash_password, load_users, save_users


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update an ARIA Mentor local auth user.")
    parser.add_argument("username", help="Login username")
    parser.add_argument("role", choices=sorted(SUPPORTED_ROLES), help="User role")
    parser.add_argument("--display-name", default=None, help="Display name")
    args = parser.parse_args()

    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        raise SystemExit("Passwords do not match.")

    if len(password) < 12:
        raise SystemExit("Password must be at least 12 characters.")

    payload = load_users()
    users = payload.setdefault("users", [])

    existing = find_user(args.username)
    new_record = {
        "username": args.username,
        "display_name": args.display_name or args.username,
        "role": args.role,
        "active": True,
        "password_hash": hash_password(password),
    }

    if existing:
        for index, user in enumerate(users):
            if user.get("username", "").lower() == args.username.lower():
                users[index] = new_record
                break
        action = "updated"
    else:
        users.append(new_record)
        action = "created"

    save_users(payload)
    print(f"User {args.username} {action} with role {args.role}.")


if __name__ == "__main__":
    main()
