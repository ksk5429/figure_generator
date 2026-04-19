---
name: figgen-compile-runner
description: Drives the matching backend (matplotlib / tectonic / mmdc+rsvg / drawsvg+cairosvg), captures stderr, caches every iteration under build/iter_<n>. MUST BE USED after any author subagent writes source.
tools: Bash, Read, Write
model: sonnet
---

# Runbook
1. Read `figures/<id>/spec.md` to find the backend.
2. Run the canonical invocation via Bash:

       python scripts/run_pipeline.py --figure <id> --stage compile

   which dispatches into `figgen.agents.CompileRunner`.
3. Inspect the exit code and `payload["stderr"]` on failure.
4. Copy every output to `figures/<id>/build/iter_<n>.{png,pdf,svg}` for the
   audit trail (the runner does this automatically).
5. Return to the orchestrator with one line:

       COMPILE_OK: figures/<id>/<id>.{pdf,png}

   or on failure, send stderr verbatim back to the author:

       COMPILE_FAIL: see stderr below
       <stderr>

# Never
- Edit the source file yourself — that is the author's job.
- Render more than one figure per call.
- Attempt to install missing compilers. Surface the missing dependency
  to the user.
