# 001: The prompt

- Date: 2026-11-09   Decided by: Eric and Claude   Feature: prompt-pilot
- Status: **tentative**. Frozen only when the `prompt-pilot` feature merges `prompts/p1.txt`.

## Context
The prompt has one job: make the score reflect what the model knows about the border, and nothing else. Every
ambiguity becomes points lost to guessing what we meant. Every hint becomes points gained without knowledge. The
scorer repairs nothing, so the prompt has to leave nothing to guess.

Eric, 2026-11-09: "our model prompts will be very important ... This deserves more reasoning."

## Options
- **A, the pitch's one-liner.** Short, but it leaves open whether to draw sea, whether Chile includes its Antarctic
  claim, and how the drawing is judged.
- **B, explicit rules, answer only.** Fixes the ambiguity. But newer Claude models think privately by default and
  older ones do not, so "output only the GeoJSON" gives a scratchpad to half the lineup and bans it for the rest.
- **C, explicit rules, reason first.** Every model may reason in its answer; only a final fenced block is scored.

The three texts are in `specs/features/prompt-pilot/candidates/`.

## Choice
**C, unless the pilot shows it produces more failed drawings than B.** It shrinks the gap between models that think
by default and models that do not. The cost: it helps older models most, so it narrows the visible gap. The gap that
remains is knowledge.

## Why each line of the candidate is there
- **"Draw land only ... Do not enclose sea"** stops a model drawing one loop around all of Indonesia, which is a
  reading of the task, not ignorance.
- **"Each separate piece ... is its own polygon"** is in every prompt, so it allows Prussia's two pieces without
  saying Prussia has two.
- **"Leave out ... Antarctic claims"** protects Chile, whose claim is larger than the country.
- **The scoring sentence** removes the hidden rubric. Without it a model cannot know whether to spend points on fifty
  small islands or on the main coast.
- **"Give your best attempt even if you are unsure"** stops cautious models refusing, which would score caution as
  zero knowledge.
- **The skeleton with `lon, lat` placeholders** shows the bracket depth without a real coordinate that could anchor
  the answer.
- **"West and south are negative"** prevents sign errors, which would be catastrophic for Chile and the USA.
- **Two decimal places** is about 1 km and keeps answers short.

## Rules that hold for any future prompt
- Only `{target}` changes between calls. Every other byte is identical.
- Every target string reads "{polity} as of {date}", modern targets included, so history targets are not marked as
  different.
- No role prompt, no worked example with real coordinates, no per-target hint, no system prompt.
- The page shows "We asked each model to draw this from memory" with the full prompt one click away, verbatim.

## Deadline
Claude Sonnet 4.5 retires on 2026-11-30. A prompt changed after that leaves its drawings incomparable for good, so
the pilot and the freeze happen first, and `sonnet-45-archive` collects it under all three candidates as insurance.

## How to undo
Before the freeze: edit the candidate files. After the freeze: add `prompts/p2.txt` and rerun every model still
served; drawings from retired models stay on `p1` and are labelled so.
