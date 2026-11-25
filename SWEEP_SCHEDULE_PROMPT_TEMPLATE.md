# Daily sweep — copy/paste setup

**Instructions:** replace the two bracketed placeholders below (`<YOUR_FOLDER_PATH>` and `<TIME>`), then paste the entire message (everything under the line) to your own Cowork/Claude Code assistant, in a session that has Outlook, Slack, and Zoom connected. It will create the scheduled task for you — nothing else to configure.

- `<YOUR_FOLDER_PATH>` — the full path to your personal SuccessIQ folder, e.g. `/Users/janedoe/Library/CloudStorage/OneDrive-project44/SuccessIQ`
- `<TIME>` — when you want it to run each day, e.g. "9:00 AM" or "3:00 PM"

---

Set up a daily scheduled task called `successiq-daily-sweep` that runs every day at <TIME> with exactly this prompt:

````
Run a SuccessIQ sweep for the last 48 hours and update the successiq.json database.

## Objective
Pull customer signals from Outlook (received + sent), Clari post-call summaries, Slack, and Zoom for the past 48 hours or from the time last run was successful. Synthesize findings, write a Python patch script, execute it against the live database, and deliver a sweep report.

## Database location
<YOUR_FOLDER_PATH>/successiq.json

Backups go to the backups/ subfolder in the same directory. Sweep reports go to the "Sweep Reports" subfolder in the same directory.

## Steps

1. **Load the database** — read successiq.json and note current task count, customer count, contact count, and highest task ID. Confirm the file is present before proceeding.

2. **Search Outlook received** — `outlook_email_search` for the last 48 hours or the last time when the run was successful. Look for: customer emails, support ticket notifications (Zendesk/Salesforce), escalations, renewal signals, inbound churn signals, SAP case notifications, invoice/collections notices.

3. **Search Outlook sent** — equally important. Sent mail reveals commitments made, next steps promised, accounts handed over, escalations raised. Search last 48 hours.

4. **Search Clari** — `outlook_email_search` from:notifications@clari.com for the last 48 hours. Clari post-call summaries contain action items, decisions, and customer signals that exist nowhere else. Read each summary carefully.

5. **Search Slack** — search for customer names and key topics from the last 48 hours.

6. **Check Zoom** — `search_meetings` for the last 48 hours. For any meeting with `has_summary: true` and external attendees, call `get_meeting_assets` to retrieve the AI summary and action items.

7. **Synthesize findings** — identify:
   - New tasks to create
   - Existing tasks to update (progress, notes, subtasks, status)
   - Tasks to close (completed or transferred)
   - Customer stage/health/risk/next changes
   - New contacts to add
   - Update the customer summary with old context and new data
   - Contact lastContacted updates

7b. **Apply the CS methodology — Lincoln Murphy / Sixteen Ventures (required, not optional).** This sweep is not just a data-extraction pass — every task and stage change below must be reasoned through this framework:
   - **Desired Outcome / Required Outcome**: Customer Success means the customer achieves their Required Outcome (their actual business goal) — not just that a product question got answered. Before writing any task's `ctx`, ask: *what business result is this customer trying to achieve, and how does this task serve or unblock it?* A `ctx` that just restates the triggering email without naming the Required Outcome is incomplete — rewrite it.
   - **Success Vector (direction, not a snapshot)** — this is what `stage` encodes:
     - Positive (engaging, progressing, expanding) → `stage: Expansion` or `Healthy`
     - Neutral (stalled, flat renewal, not growing) → `stage: Steady`, and create a re-engagement task
     - Negative (Required Outcome at risk, signals emerging) → `stage: At-risk`, intervene now
     - Ghost (key contact dark, no response) → `stage: At-risk`, P0 task, escalate
   - Only change `stage` on a real evidence pattern (two or more consistent signals, or one unambiguous one like a signed termination or confirmed renewal). Never flip `stage` on a single good or bad email.
   - **Priority (`pri`) must follow from Required Outcome / Success Vector status**, not from how urgent the email sounded:
     - P0 — Required Outcome blocked / account trending Ghost or At-risk — act today
     - P1 — Success Milestone at risk, renewal imminent, contractual obligation
     - P2 — proactive expansion/retention at a milestone (positive vector)
     - P3 — relationship maintenance (neutral vector, regular cadence)
     - P4 — pure admin
   - When a sweep reveals a new or changed business goal, update the customer `summary` to capture that Desired Outcome itself, not just the activity that revealed it.

8. **Write and execute a Python patch script** — follow this pattern:
   - Back up successiq.json to backups/successiq_before-sweep-{timestamp}.json before any write
   - Use helper functions: find_task(id), find_customer(slug), find_contact_by_name(frag), append_note(obj, text), next_task_id(), next_audit_id()
   - next_audit_id() must handle entries without "id" key (some use "timestamp"/"ts"/"op") — use try/except
   - Valid stage values: Expansion | Steady | At-risk | Healthy (never "Active")
   - append_note() format: "[YYYY-MM-DD SWEEP] <evidence and action>"
   - New tasks need: id, cust, title, pri, owner, status, created, due, durationDays, ctx, subs (min 2), prog, notes, tags
   - Update the customer summary with old context and new data
   - Append one auditLog entry summarizing the sweep
   - Save with json.dump(data, f, ensure_ascii=True, indent=2)
   - Verify counts after write

9. **Build the sweep report** using this format:

```
## SWEEP REPORT — [date range]

### Highlights
[Only if something material: new P0, at-risk transition, churn signal, renewal signal, major escalation. 0–3 items max. Skip section if nothing rises to this bar.]

### Tasks updated
[Group by priority P0 → P4. One line per task: #ID ACTION: title — one-line evidence]

### Customer updates
[One line per customer with any change]

### Activity summary
- Customers touched: N
- New contacts added: N
- auditLog entries appended: N
- Backups kept: N
- Outlook checked : Yes/No
- Outlook sent emails checked : Yes/No
- Slack verified : Yes/No
```

10. **Write the report to disk (required)** — save the exact report text from step 9 to a new file named `SWEEP_REPORT_<start>-<end>.md` (e.g. `SWEEP_REPORT_2026-10-16-18.md`, matching the date range covered) inside the "Sweep Reports" subfolder next to successiq.json (`<YOUR_FOLDER_PATH>/Sweep Reports/`). Create that subfolder first if it doesn't exist. This file is read automatically by the SuccessIQ dashboard's "Sweep summary" view, which always shows whichever SWEEP_REPORT_*.md file in that folder has the newest modification time — so writing a new one each run is what keeps that view current. Do not delete or overwrite prior SWEEP_REPORT_*.md files; each run adds a new one. Then deliver the same report as your final message.

## Key schema notes
No `meta` object exists in this schema — update the top-level `exported` ISO timestamp on every write instead.
- Task fields: id (int), cust (customer slug — not customer_id), title, pri (P0–P4 — not priority), owner, status (open/completed), created, due, durationDays, ctx (must name the Required Outcome — see 7b), subs [{t, done}], prog (0-100), notes, contactIds, tags
- Customer fields: id (slug — this IS the foreign key, there's no separate numeric id), name, stage (Expansion/Steady/At-risk/Healthy — the Success Vector field, see 7b), sentiment (Green/Yellow/Red — a SEPARATE account-health indicator, don't conflate with stage), health (0-100), arr/mrr, seg/segment, industry, region, next, risk, summary, notes. Many customer records also carry CRM metadata (contractExp, renewalFQ, forecast, churnRisk, tenantIds, accountId, etc.) — never drop or blank fields you don't recognize, only touch what your evidence supports.
- Contact fields (top-level `contacts` array, not nested under customers): id (int), name, cust (slug), designation, country, email, eb (bool — true if Economic Buyer), lastContacted, notes. There is no `role` field — use `designation` and the `eb` boolean instead.
- auditLog fields: id (string, numeric), ts (ISO datetime), actor, action, details, custId

## Constraints
- Never push or merge to master/main branch
- Never delete database records — only add or update by rewriting it with complete context
- Prefer updating existing tasks over creating new ones when the evidence is an update to something already tracked
- Do not create duplicate tasks for the same customer issue
- Do not assume anything
- Do not miss the sent emails
- Always hold the current context from backup while doing new search to relate the correct details
````
