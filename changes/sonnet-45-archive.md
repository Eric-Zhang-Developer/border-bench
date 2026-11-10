## What shipped
99 raw answers from Claude Sonnet 4.5: eleven targets, three prompt candidates (A, B, C), three samples each, collected on 2026-11-10 UTC before the model retires on 2026-11-30. No refusals, no empty answers, none cut off. Cost: $5.75 from the run files.

## Where it lives
`runs/archive/targets.toml` (the eleven target names), `runs/archive/pilot-{a,b,c}/claude-sonnet-4-5-20250929/<target>/<n>.json`, `runs/archive/overview.png` (an unscored picture of all 99).

## How to check it
verify: `python3 pipeline/verify.py` pass at f8a791f
`find runs/archive -name '*.json' | wc -l` -> 99.

## Gaps
33 of the 99 answers (9 under A, 7 under B, 17 under C) were collected before the runner recorded timing, so they have no `started_at`, `first_token_ms`, `first_text_ms`, `duration_ms` or `attempts`. They were not asked again. 18 answers are not valid JSON as the model wrote them (15 under B, 3 under C); they are saved as written and it is the scorer's rule that decides what they count as. Nothing is scored here. The overview picture was drawn by a throwaway script that is not in the repo.
