---
name: Three prompts are compared on real drawings and one is frozen
depends_on: [runner, scorer]
owns: [runs/pilot/, prompts/, sheets/pilot/]
assignee: "eric-1"
---

# Prompt pilot

The reasoning behind the three candidates is in `specs/decisions/001-prompt.md`. The three texts are in `candidates/`
in this folder. The decision to freeze is in `specs/decisions/prompt-pilot-freeze.md`.

## Plan
1. Compare the three candidates on real drawings.
2. Show the maintainer the drawings and the numbers. **The maintainer picks.**
3. Copy the chosen candidate to `prompts/p1.txt`.

## What happened instead of the planned 36-call pilot
The plan was a separate pilot: three models, two targets, three candidates, two tries each. It was not run. By the
time it could have been, the comparison already existed:
- The Sonnet 4.5 archive (`runs/archive/`) holds that model under all three candidates on eleven targets. The four
  with a true border were scored: 36 drawings (`specs/features/scorer/archive-*.png`, pull request 29).
- A first look ran Claude Fable 5.2 under candidate C on the same four targets (`sheets/pilot/`, pull request 32).

The maintainer looked at those and chose C on 2026-11-09. The pilot as planned would have cost more calls and waited
for the Prussia border, to answer a question the archive had mostly answered.

## Requirements
- `prompts/p1.txt` is a byte-for-byte copy of `candidates/c.txt`. Once merged it is never edited.
- A new prompt is a new id (`p2`) and a full rerun, as `specs/decisions/001-prompt.md` says.
- This pull request is a one-way door and human-reviewed.

## Validation
- `cmp prompts/p1.txt specs/features/prompt-pilot/candidates/c.txt` -> no output.
- The evidence is on main and reproducible with no model call:
  `uv run python -m pipeline.sheet runs/archive pilot-a,pilot-b,pilot-c usa` (and `chile`, `indonesia`, `croatia`).

## Defaults
None. The choice is the maintainer's.
