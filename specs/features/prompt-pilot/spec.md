---
name: Three prompts are compared on real drawings and one is frozen
depends_on: [runner, scorer, truth-history]
owns: [runs/pilot/, prompts/, sheets/pilot/]
assignee: "eric-1"
---

# Prompt pilot

The reasoning is in `specs/decisions/001-prompt.md`. The three texts are in `candidates/` in this folder.

## Plan
1. Run the pilot: Sonnet 4.5, Haiku 4.5 and the newest Opus × Indonesia and Prussia × candidates A, B, C × 2
   samples = 36 calls.
2. Score them and make one contact sheet per target and candidate in `sheets/pilot/`.
3. Open the PR with the sheets and the table below. **Eric picks.** Then add `prompts/p1.txt` to the same PR.

## Requirements
- The PR reports, per candidate: failed drawings, drawings that enclose sea, swapped or wrongly signed coordinates,
  the range of point counts, and median overlap % per model.
- It answers one question in plain words: does C beat B on the models that do not think by default?
- `prompts/p1.txt` is a byte-for-byte copy of the chosen candidate. Once merged it is never edited.
- This PR is a one-way door and human-reviewed: it does not merge without Eric.
- If Eric wants a wording change, edit the candidate, rerun the pilot for it, and rerun `sonnet-45-archive` for the
  new text. All of that must finish before 2026-11-30.

## Validation
- `find runs/pilot -name '*.json' | wc -l` -> 36.
- Six contact sheets embedded in the PR.
- `cmp prompts/p1.txt specs/features/prompt-pilot/candidates/<chosen>.txt` -> no output.

## Defaults
None. The choice is Eric's.
