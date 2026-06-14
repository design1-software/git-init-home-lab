# AI Mentor + Zammad Phase 6 and Phase 7 Test Runbook

This runbook covers the final two automation phases for the Help Desk / Ticketing domain.

## Phase 6: Instructor-approved Zammad writeback

Goal: after a student produces a valid final ticket note in AI Mentor, the instructor can approve one controlled note writeback to Zammad.

### Rules

- Instructor approval is required.
- The writeback adds one note/article to Zammad.
- The writeback does not close the Zammad ticket.
- The writeback does not change ticket priority.
- The writeback does not reassign the ticket.
- The local ARIA assignment is marked completed after writeback.
- Duplicate writeback is blocked when an assignment is already approved and completed.

### Required inputs

- `assignment_id`
- numeric `zammad_ticket_id` if it is not already stored on the assignment
- final instructor-approved note text

### API endpoint

```bash
curl -X POST http://127.0.0.1:8081/review/queue/<ASSIGNMENT_ID>/approve \
  -H 'Content-Type: application/json' \
  -b /tmp/aria-cookie.txt \
  -d '{
    "zammad_ticket_id": "<ZAMMAD_TICKET_ID>",
    "approved_text": "Summary:\n...approved final note text..."
  }'
```

The authenticated user must be an instructor or admin.

### Expected result

- A Zammad note/article is created.
- The local assignment status becomes `completed`.
- The response says the Zammad ticket state was not changed.

## Phase 7: Instructor-created lab tickets from ARIA

Goal: instructor creates a Zammad ticket and matching local ARIA assignment from a lab template.

### Script

```bash
/opt/aria-ai-mentor/source/git-init-home-lab/services/ai-mentor/scripts/create_lab_ticket.py
```

### Example: create Ticket-001 for Dominique

```bash
cd /opt/aria-ai-mentor/source/git-init-home-lab
python3 services/ai-mentor/scripts/create_lab_ticket.py \
  --student student02 \
  --template ticket-001-dns-failure \
  --created-by instructor
```

### Example: create Ticket-001 for Sha Neal

```bash
cd /opt/aria-ai-mentor/source/git-init-home-lab
python3 services/ai-mentor/scripts/create_lab_ticket.py \
  --student student01 \
  --template ticket-001-dns-failure \
  --created-by instructor
```

### Optional arguments

```bash
--group "Users"
--priority "2 normal"
--due-date "YYYY-MM-DD"
--extra "Instructor note here"
```

### Expected result

The script prints:

```text
Zammad ticket created and ARIA assignment linked.
Zammad ticket number: <number>
Zammad ticket id: <id>
Zammad URL: <url>
Assignment ID: <assignment_id>
Student: <student>
Lab ticket ID: <ticket_id>
```

Then the student should sign into AI Mentor and click:

```text
Load My Zammad Tickets
```

The new ticket should appear automatically.

## Deployment after pulling repo updates

Run inside CT 120:

```bash
cd /opt/aria-ai-mentor/source/git-init-home-lab
git pull
cp -r services/ai-mentor/app/* /opt/aria-ai-mentor/app/
cp -r services/ai-mentor/lab_templates /opt/aria-ai-mentor/
systemctl restart aria-ai-mentor
curl http://127.0.0.1:8081/health
```

Make sure `/opt/aria-ai-mentor/.env` includes:

```env
ZAMMAD_BASE_URL=http://100.71.47.90:8080
ZAMMAD_WEB_URL=http://100.71.47.90:8080
ZAMMAD_DEFAULT_GROUP=Users
ZAMMAD_API_TOKEN=<existing token>
```
