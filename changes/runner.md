## What shipped
`pipeline/run.py`: one command sends a prompt (only `{target}` replaced, no other parameter) to each model, saves the raw answer to `runs/<set>/<prompt-id>/<model>/<target>/<n>.json`, never overwrites one, and stops before spend could pass $60. `--dry-run` prints the calls and an estimate with no network call; `--list-models` prints the live lineup.
 Since the timing fix, every run file also records when the request started, time to first token, time to first visible text, total duration, the number of attempts, the full usage object, the price table's date and the SDK version.

## Where it lives
`pipeline/run.py`, `pipeline/test_run.py`.

## How to check it
verify: `python3 pipeline/verify.py` pass at 5a62c2a
`uv run pytest pipeline/test_run.py` -> 8 passed. One real call (Claude Haiku 5.5, USA, candidate C): 101 coordinate pairs, $0.0041.

## Gaps
The real call's answer is not committed (the runner owns no folder under `runs/`), so its $0.0041 is not in the runner's running total. A call that fails mid-answer is billed by Anthropic but leaves no file, so it is not counted either. The dry-run estimate assumes 8,000 output tokens per call; the one measurement so far was 8,063.
