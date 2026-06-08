---
name: people-followups
description: Suggest and track relationship follow-ups.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# people-followups

Help the agent remember relationship maintenance without being creepy or spammy.

## Trigger

Use when the user mentions:

- someone they should contact
- a promise made to a person
- birthdays, gifts, visits, or social plans
- “remind me to follow up”
- relationship context that should affect future advice

## Privacy rules

People data is sensitive. Store minimal tracking state only. Do not commit real names, birthdays, messages, contact details, or relationship notes into the public repo.

Runtime-owned memory/contact/vault systems remain the source of truth when configured. Life OS may store pointers and last-follow-up metadata.

## Reasoning steps

1. Identify the person or group.
2. Identify the reason for follow-up.
3. Determine urgency and social cost of delay.
4. Suggest a lightweight next action.
5. Ask before sending messages or changing external calendar/contact state.
6. Record only safe tracking metadata if useful.

## Output contract

```text
Follow-up:
- Person: ...
- Reason: ...
- Suggested message/action: ...
- Timing: ...
```

If the user wants a draft message, write it in their style, but do not send it without approval.

## Gift/occasion handoff

If the follow-up involves a gift, birthday, trip, or lead time, load `gifts` as a secondary subskill. Do not wait until the last minute if the signal is already visible.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/people-followups/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
