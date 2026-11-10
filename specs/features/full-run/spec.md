---
name: Every Claude model draws all six targets with the frozen prompt
depends_on: [prompt-pilot]
owns: [runs/p1/, results/, sheets/p1/]
assignee: "eric-1"
---

# Full run

Run in two stages, so the maintainer sees real strips before most of the money is spent. Maintainer, 2026-11-09: "run maybe only
Haiku 5.5, Sonnet 5.5, and probably Sonnet 4.5. Then I can see a shape of what's going on instead of us doing a full
... run when I have no eyes on what's going on."

## Plan
1. **Stage 1, the preview.** `--dry-run`, then run Claude Sonnet 4.5, Claude Haiku 5.5 and Claude Sonnet 5.5 on the
   six targets with `prompts/p1.txt`, three samples each: 54 calls.
2. Score, write `results/results.json`, make one contact sheet per target in `sheets/p1/`, and open the stage 1 PR
   (`feat(full-run): ...`, no done note yet). It merges on green like any other.
3. **Stop and ask.** File a `needs-human` issue titled "Preview strips are in: run the other models?" with what
   Requirements lists. Make no stage 2 call until the maintainer says go, in that issue or in chat.
4. **Stage 2.** Every other listed model: three samples, one for the Fable models. Rescore, remake the sheets, write
   the done note, open the stage 2 PR.

## Requirements
- Sonnet 4.5 runs first, in stage 1.
- The three preview models span the lineup: the oldest model served, the cheapest current one, and the same tier as
  the oldest one generation later. Stage 1 answers are final `p1` runs. Stage 2 never requests them again.
- The stage 1 issue gives the maintainer what they need to decide:
  - the six contact sheets, with one plain sentence under each on what the strip shows;
  - failed drawings, refusals, and answers that hit `max_tokens`, per model;
  - **measured** dollars per call for each of the three models, and from those a projected cost for stage 2, set
    against what is left under the cap. This replaces the planning estimate, which was never measured;
  - anything that looks wrong with a score, a border or the prompt. A wrong-looking result is a reason to stop, not a
    detail to fix quietly.
- If the maintainer asks for a change that alters scores (prompt, grading, a border), stage 1 is redone under the new setup
  before stage 2 starts; say what that costs first.
- If the projected stage 2 cost does not fit under the cap, say so in the issue and propose which models to run with
  one sample. Do not raise the cap.
- If the spend cap stops a run, commit what exists, say which models and targets are missing, and file a
  `needs-human` issue.
- Pilot or archive answers are not reused as `p1` runs, even where the prompt text is identical.

## Validation
- After stage 1: 54 run files under `runs/p1/`; `uv run python -m pipeline.score` writes `results/results.json` and a
  second run produces no diff; six contact sheets embedded in the PR and in the issue.
- After stage 2: run files total 6 targets × (12 models × 3 + 3 models × 1) = 234, or the count the live model list
  implies, stated in the PR; six contact sheets with every model.
- Each PR states dollars spent, refusals, failed drawings, and every model whose answers hit `max_tokens`.

## Defaults
A model that appears on the Models API after a stage starts is left for a later `fix(full-run)` PR.
