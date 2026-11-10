---
name: Claude Sonnet 4.5's drawings are saved before it retires
depends_on: [runner]
owns: [runs/archive/]
assignee: "eric-1"
---

# Sonnet 4.5 archive

Claude Sonnet 4.5 retires on 2026-11-30. It is the oldest model still served, so it is the start of every strip.
After it retires, nothing new can be asked of it.

## Plan
1. Write `runs/archive/targets.toml` with the eleven target names below.
2. Run Sonnet 4.5 on all eleven, under candidates A, B and C, three samples each: 99 calls.
3. If the Models API lists any other model with a retirement date before 2027, archive it the same way and say so.

## Requirements
- Target names, exactly:
  - the contiguous United States (the lower 48 states) as of 1 January 2024
  - Chile as of 1 January 2024
  - Indonesia as of 1 January 2024
  - Croatia as of 1 January 2024
  - the Kingdom of Prussia as of 1 January 1816
  - Poland as of 1 January 1938
  - Australia as of 1 January 2024
  - China as of 1 January 2024
  - Egypt as of 1 January 2024
  - the Roman Empire as of 1 July 117
  - Mexico as of 1 January 1830
- Prompts: `specs/features/prompt-pilot/candidates/a.txt`, `b.txt`, `c.txt`, with ids `pilot-a`, `pilot-b`,
  `pilot-c`.
- No scoring here. Truth for the last five targets does not exist yet.
- If the candidates change before the freeze, rerun this feature for the new text while the model is still served.

## Validation
- `find runs/archive -name '*.json' | wc -l` -> 99.
- Every file has a non-empty `raw` or a recorded stop reason; the PR lists any refusals.
- The PR states the dollars spent, from the run files.

## Defaults
Africa 1914 and the Holy Roman Empire are not archived: their prompt does not exist yet.
