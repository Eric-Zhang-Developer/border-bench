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
1. **Stage 1, the preview.** `--dry-run`, then run Claude Sonnet 4.5, Claude Haiku 5.5 and Claude Sonnet 5.5 with
   three samples each, and Claude Fable 5.2 with one, using `prompts/p1.txt`.
   - **Stage 1a, the four modern targets** (usa, chile, indonesia, croatia): 40 calls. Run on 2026-11-10, because the
     maintainer asked for real strips before the history borders were ready (Maintainer, 2026-11-09: "let's do that",
     approving this plan as the planning session put it to them).
   - **Stage 1b, Prussia and Poland**, when their true borders are on `main`: the same four models, 20 calls.
     Stage 1a answers are not asked for again. Run on 2026-11-10 in the same pass as stage 2: the two borders landed
     while stage 2 was running, after the maintainer's go, so a separate PR would only have split one night's answers.
2. Score, write `results/results.json`, make one contact sheet per target in `sheets/p1/`, and open the stage 1 PR
   (`feat(full-run): ...`, no done note yet). It merges on green like any other.
3. **Stop and ask.** File a `needs-human` issue titled "Preview strips are in: run the other models?" with what
   Requirements lists. Make no stage 2 call until the maintainer says go, in that issue or in chat.
4. **Stage 2.** Every other listed model: three samples, one for the Fable models. Rescore, remake the sheets, write
   the done note, open the stage 2 PR. Maintainer, 2026-11-09, on issue 36's option A: "Run all eleven".
   - Cheapest models first. Claude Opus 5 and Claude Opus 5.5 had never been measured, so each starts with one call.
   - **Claude Opus 5 is held after its one call** (United States: 29,230 output tokens, 369 seconds, $0.73, more than
     Claude Fable 5.2 on the same target). Issue 36 said the run would stop and ask in that case. Its answer is on
     the branch `full-run-opus-5`; its other 17 calls, the done note and the last 18 run files wait for the
     maintainer's answer (three samples, or one like the Fable models).

## Requirements
- Sonnet 4.5 runs first, in stage 1.
- The three preview models span the lineup: the oldest model served, the cheapest current one, and the same tier as
  the oldest one generation later. Claude Fable 5.2, the newest, was added with one sample at the maintainer's
  request. Stage 1 answers are final `p1` runs. Stage 2 never requests them again.
- Money (Maintainer, 2026-11-09: "so i don't go broke"): the dry run is priced from measured tokens per drawing, not
  the planning guess, and nothing is called if it comes to more than $10 without asking first. Models that think for
  minutes run at most two calls at a time. If a call is lost (paid for, no file saved: issue 31), the run stops and
  the loss is reported; it is not retried.
- The stage 1 issue gives the maintainer what they need to decide:
  - the contact sheets (four after stage 1a, six after 1b), with one plain sentence under each on what the strip
    shows;
  - failed drawings, refusals, and answers that hit `max_tokens`, per model;
  - **measured** dollars per call for each stage 1 model, and from those a projected cost for stage 2, set
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
- After stage 1a: 40 run files under `runs/p1/` (4 targets × (3 models × 3 + 1 model × 1)); `uv run python -m
  pipeline.score` writes `results/results.json` and a second run produces no diff; four contact sheets embedded in
  the PR and in the issue.
- After stage 1b: 60 run files, six contact sheets.
- After stage 2: run files total 6 targets × (12 models × 3 + 3 models × 1) = 234, or the count the live model list
  implies, stated in the PR; six contact sheets with every model. (Fable 5.2's six are already among them.)
  While Claude Opus 5 is held the count is 216 (14 models); it reaches 234 if the maintainer gives it three samples,
  222 if one.
- Each PR states dollars spent, refusals, failed drawings, and every model whose answers hit `max_tokens`.

## Defaults
A model that appears on the Models API after a stage starts is left for a later `fix(full-run)` PR.
