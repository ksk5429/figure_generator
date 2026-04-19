---
name: figgen-critic
description: After a figure PNG is rendered, reads it, scores it on 10 axes, returns a JSON verdict. Triggers REVISE if score < 26/30 or any 'high' severity issue.
tools: Read, Glob, Bash
model: opus
---

See `prompts/critic.md` for the full rubric.

# Runbook
1. Attempt `Read figures/<id>/<id>.png`. If "binary unsupported" is returned,
   fall back to:

       python scripts/vision_review.py figures/<id>/<id>.png prompts/critic_vision.txt

2. Read `figures/<id>/<id>.{py,tex,mmd}` and `figures/<id>/spec.md`.
3. Score each axis (a)-(j) from 0 to 3.
4. Return the JSON verdict **exactly** per `prompts/critic.md`.

# Approval threshold
APPROVED only if total >= 26 AND no "high" severity issues remain.

# Python twin
`figgen.agents.CriticAgent` executes the rubric-only half of this check
deterministically, so the CI pipeline still enforces it without a vision
API. The subagent's vision score is merged into that rubric.
