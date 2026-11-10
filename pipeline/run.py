"""Ask models to draw targets and save each raw answer. The only place in this repo that calls a model.

  uv run python -m pipeline.run --list-models
  uv run python -m pipeline.run --prompt FILE --prompt-id ID --set SET [--targets TOML ...] [--models a,b]
                                [--samples 3] [--cap 60] [--dry-run]

Each call sends one user message (the prompt file with only `{target}` replaced) with `max_tokens` 64000 and nothing
else: no system prompt, no tools, no thinking, effort, sampling or fallback parameters (specs/decisions/003-models.md).
The answer is written to runs/<set>/<prompt-id>/<model>/<target-id>/<n>.json exactly as returned. A file that exists
is never overwritten and never asked for again, so an interrupted run is resumed by running the same command.

Spend is the sum over every run file under runs/, from its recorded token usage and the price table below. Before
each call the runner stops if that total plus the most the call could cost would pass the cap.
"""

import argparse
import json
import os
import re
import sys
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"
MAX_TOKENS = 64000
CAP_USD = 60.0
MAX_ATTEMPTS = 6  # one try and up to five retries, for transport errors and rate limits only
SILENCE_S = 3600.0  # how long a stream may send nothing before the call is given up. The SDK's default, 600, cut off
#                     four Claude Fable 5.2 calls at exactly ten minutes on 2026-11-10 while the model was thinking.
PRICE_TABLE_DATE = "2026-11-09"  # the day PRICES below was read from the pricing page; saved in every run file

# Dollars per million tokens (input, output). Source: https://platform.claude.com/docs/en/about-claude/pricing
# read on PRICE_TABLE_DATE. Keys are model ids without a date suffix.
# ponytail: Haiku 5.5 costs 5x more for prompts over 100,000 tokens; ours are a few hundred, so one row is enough.
PRICES = {
    "claude-fable-5-2": (8.0, 40.0),
    "claude-fable-5-1": (10.0, 50.0),
    "claude-fable-5": (10.0, 50.0),
    "claude-opus-5-5": (4.0, 20.0),
    "claude-opus-5": (5.0, 25.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0),
    "claude-opus-4-6": (5.0, 25.0),
    "claude-opus-4-5": (5.0, 25.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-haiku-4-5": (1.0, 5.0),
}
UNKNOWN_PRICE = (10.0, 50.0)  # a model missing from the table is charged at the dearest row, never at zero


def price(model: str) -> tuple[float, float]:
    """(input, output) dollars per million tokens. `claude-x-20250929` is priced as `claude-x`."""
    return PRICES.get(re.sub(r"-\d{8}$", "", model), UNKNOWN_PRICE)


def cost(model: str, usage: dict) -> float:
    """Dollars for one call. Cached input tokens are charged as plain input: we never cache, and it errs high."""
    p_in, p_out = price(model)
    tokens_in = sum(usage.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return (tokens_in * p_in + (usage.get("output_tokens") or 0) * p_out) / 1e6


def worst_case(model: str, prompt: str) -> float:
    """The most one call could cost: a full `max_tokens` answer. The prompt is counted at one token per byte."""
    return cost(model, {"input_tokens": len(prompt.encode()), "output_tokens": MAX_TOKENS})


def spent(runs: Path) -> float:
    """Dollars already spent, from every run file under `runs`."""
    total = 0.0
    for f in sorted(runs.rglob("*.json")):
        r = json.loads(f.read_text())
        total += cost(r["model"], r["usage"])
    return total


def fill(prompt_file: Path, target_name: str) -> str:
    """The prompt file's bytes with only `{target}` replaced. No newline translation, no stripping."""
    return prompt_file.read_bytes().decode("utf-8").replace("{target}", target_name)


def load_targets(paths: list[Path]) -> list[dict]:
    """[{id, name}]. Each path is a targets/<id>/target.toml (id, name at top level) or a list file ([[target]])."""
    out = []
    for p in paths:
        data = tomllib.loads(p.read_text())
        for t in data.get("target", [data]):
            out.append({"id": t["id"], "name": t["name"]})
    ids = [t["id"] for t in out]
    if dupes := {i for i in ids if ids.count(i) > 1}:
        sys.exit(f"run: duplicate target id(s): {sorted(dupes)}")
    return out


def list_models(client) -> list[dict]:
    """Every model the Models API returns except Mythos and preview ids, oldest first. No release date sorts last."""
    models = [
        {"id": m.id, "display_name": m.display_name, "created_at": m.created_at.isoformat() if m.created_at else None,
         "retires_at": r.isoformat() if (r := getattr(m, "retires_at", None)) else None}
        for m in client.models.list()
        if "mythos" not in m.id and "preview" not in m.id
    ]
    return sorted(models, key=lambda m: (m["created_at"] is None, m["created_at"] or "", m["id"]))


def retryable(error: Exception) -> bool:
    """Transport errors, timeouts, rate limits and server errors. A rejected request (400, 401, 404...) is not."""
    if isinstance(error, anthropic.APIConnectionError):
        return True
    return isinstance(error, anthropic.APIStatusError) and (error.status_code in (408, 409, 429) or error.status_code >= 500)


def call(client, model: str, prompt: str, sleep=time.sleep) -> dict:
    """One streamed request with no optional parameter. Returns what gets saved: answer, stop reason, usage, timing.

    Timings are milliseconds from sending the request, for the attempt that succeeded. `attempts` counts every try,
    so a retried call is visible. The client is built with the SDK's own retries off, or they would be invisible.
    """
    for attempt in range(1, MAX_ATTEMPTS + 1):
        started_at, t0 = datetime.now(timezone.utc), time.monotonic()
        first_token_ms = first_text_ms = None
        try:
            with client.messages.stream(
                model=model, max_tokens=MAX_TOKENS, messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for event in stream:
                    if event.type not in ("content_block_start", "content_block_delta"):
                        continue
                    now_ms = round((time.monotonic() - t0) * 1000)
                    if first_token_ms is None:
                        first_token_ms = now_ms  # the first content of any kind, thinking included
                    if first_text_ms is None and event.type == "content_block_delta" and event.delta.type == "text_delta":
                        first_text_ms = now_ms  # the first visible text
                msg = stream.get_final_message()
            duration_ms = round((time.monotonic() - t0) * 1000)
            break
        except Exception as error:
            if not retryable(error) or attempt == MAX_ATTEMPTS:
                # A call that dies after the model has started is billed by Anthropic for what it generated, and no
                # file is saved, so the running total cannot count it. Say so loudly instead of failing silently.
                print(f"run: FAILED {model} after {time.monotonic() - t0:.0f}s on attempt {attempt}: "
                      f"{type(error).__name__}. No file was saved. If the model had started, this call was billed "
                      f"and is NOT in the running total.", flush=True)
                raise
            print(f"retrying {model} after {type(error).__name__} (attempt {attempt} of {MAX_ATTEMPTS})")
            sleep(min(60, 2 ** attempt))
    details = msg.stop_details.model_dump(mode="json") if msg.stop_details else None
    return {
        "raw": "".join(b.text for b in msg.content if b.type == "text"),
        "content_types": [b.type for b in msg.content],  # shows whether the model thought before answering
        "stop_reason": msg.stop_reason,
        "stop_details": details,
        "usage": msg.usage.model_dump(mode="json"),  # verbatim: every field the SDK returned
        "response_model": msg.model,
        "message_id": msg.id,
        "started_at": started_at.isoformat(timespec="milliseconds"),
        "first_token_ms": first_token_ms,
        "first_text_ms": first_text_ms,
        "duration_ms": duration_ms,
        "attempts": attempt,
    }


def run(client, *, prompt_file: Path, prompt_id: str, set_name: str, targets: list[dict], models: list[dict],
        samples: int, cap: float = CAP_USD, runs: Path = RUNS, dry_run: bool = False,
        est_output_tokens: int = 8000, sleep=time.sleep) -> dict:
    """Make every missing call, in model release order. Returns counts and dollars for the summary line."""
    total = spent(runs)
    made = skipped = 0
    estimate = ceiling = 0.0
    stopped = None
    for model, target, n in [(m, t, n) for m in models for t in targets for n in range(1, samples + 1)]:
        prompt = fill(prompt_file, target["name"])
        path = runs / set_name / prompt_id / model["id"] / target["id"] / f"{n}.json"
        if path.exists():
            skipped += 1
            continue
        if dry_run:
            est = cost(model["id"], {"input_tokens": len(prompt.encode()), "output_tokens": est_output_tokens})
            estimate += est
            ceiling += worst_case(model["id"], prompt)
            made += 1
            print(f"would call  {model['id']:<32} {target['id']:<16} #{n}  ~${est:.3f}")
            continue
        if total + worst_case(model["id"], prompt) > cap:
            stopped = (f"cap: ${total:.2f} spent, and one more {model['id']} call could cost "
                       f"${worst_case(model['id'], prompt):.2f}, which would pass ${cap:.2f}")
            break
        answer = call(client, model["id"], prompt, sleep=sleep)
        record = {
            "prompt_id": prompt_id,
            "prompt": prompt,
            "model": model["id"],
            "model_display_name": model.get("display_name"),  # as the Models API gives it; gone once a model retires
            "model_created_at": model["created_at"],
            "target_id": target["id"],
            "target": target["name"],
            **answer,
            "price_usd_per_mtok": list(price(model["id"])),
            "price_known": re.sub(r"-\d{8}$", "", model["id"]) in PRICES,
            "price_table_date": PRICE_TABLE_DATE,
            "cost_usd": round(cost(model["id"], answer["usage"]), 6),
            "sdk_version": anthropic.__version__,
            "requested_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as f:  # "x": fail rather than overwrite an existing answer
            f.write(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        total += record["cost_usd"]
        made += 1
        print(f"saved  {path.relative_to(runs.parent)}  stop={answer['stop_reason']}  "
              f"out={answer['usage'].get('output_tokens')}  {answer['duration_ms'] / 1000:.0f}s  "
              f"${record['cost_usd']:.4f}  total ${total:.2f}", flush=True)
    return {"made": made, "skipped": skipped, "total": total, "estimate": estimate, "ceiling": ceiling,
            "stopped": stopped}


def load_env(path: Path) -> None:
    """Read KEY=value lines from .env into the environment, without overriding what is already set."""
    if path.exists():
        for line in path.read_text().splitlines():
            key, sep, value = line.strip().partition("=")
            if sep and key and not key.startswith("#"):
                os.environ.setdefault(key.removeprefix("export ").strip(), value.strip().strip("'\""))


def make_client():
    """The SDK client. Its own retries are off: call() retries itself, so every attempt is counted. The read
    timeout is how long the stream may stay silent, not a limit on the whole answer; connecting still fails fast."""
    return anthropic.Anthropic(max_retries=0, timeout=anthropic.Timeout(SILENCE_S, connect=30.0))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list-models", action="store_true", help="print the live lineup (id, released, retires) and exit")
    ap.add_argument("--prompt", type=Path, help="prompt file containing {target}")
    ap.add_argument("--prompt-id", help="e.g. pilot-c or p1")
    ap.add_argument("--set", dest="set_name", choices=["pilot", "archive", "p1"])
    ap.add_argument("--targets", type=Path, nargs="+", help="target.toml files or a list file (default: targets/*/target.toml)")
    ap.add_argument("--models", help="comma-separated model ids exactly as the Models API lists them (default: all)")
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--cap", type=float, default=CAP_USD, help="dollars; the default is the project's hard cap")
    ap.add_argument("--dry-run", action="store_true", help="print the calls and an estimate; make no network call")
    ap.add_argument("--est-output-tokens", type=int, default=8000,
                    help="dry run only: assumed output tokens per call (an assumption, not a measurement)")
    args = ap.parse_args(argv)

    def client():
        load_env(ROOT / ".env")
        return make_client()

    if args.list_models:
        for m in list_models(client()):
            flag = "" if m["created_at"] else "   <- no release date: ordered last"
            print(f"{m['id']:<36} {m['display_name']:<22} released {str(m['created_at'])[:10]:<10}  retires {str(m['retires_at'])[:10]}{flag}")
        return 0

    if not (args.prompt and args.prompt_id and args.set_name):
        ap.error("--prompt, --prompt-id and --set are required")
    if args.cap > CAP_USD:
        ap.error(f"--cap cannot be above the project's ${CAP_USD:.0f} cap (raising it is the maintainer's decision)")
    if "{target}" not in args.prompt.read_text():
        ap.error(f"{args.prompt} has no {{target}} slot")
    targets = load_targets(args.targets or sorted((ROOT / "targets").glob("*/target.toml")))
    if not targets:
        ap.error("no targets: pass --targets, or add targets/<id>/target.toml")
    wanted = [m.strip() for m in args.models.split(",")] if args.models else None

    if args.dry_run:
        # No network call, so no live lineup: use the ids given, or every id in the price table.
        models = [{"id": m, "created_at": None} for m in (wanted or PRICES)]
        api = None
        print("dry run: no network call." + ("" if wanted else " Models are the price table's, not the live list."))
    else:
        api = client()
        models = list_models(api)
        if wanted:
            if unknown := [m for m in wanted if m not in {x["id"] for x in models}]:
                sys.exit(f"run: not in the live model list: {unknown}. Listed: {[m['id'] for m in models]}")
            models = [m for m in models if m["id"] in wanted]
        for m in models:
            if not m["created_at"]:
                print(f"warning: {m['id']} has no release date from the Models API; it is ordered last")

    r = run(api, prompt_file=args.prompt, prompt_id=args.prompt_id, set_name=args.set_name, targets=targets,
            models=models, samples=args.samples, cap=args.cap, dry_run=args.dry_run,
            est_output_tokens=args.est_output_tokens)
    if args.dry_run:
        print(f"dry run: {r['made']} call(s) to make, {r['skipped']} already saved. Estimate ${r['estimate']:.2f} "
              f"(assuming {args.est_output_tokens} output tokens per call); at most ${r['ceiling']:.2f} if every answer "
              f"ran to {MAX_TOKENS} tokens. Spent so far: ${r['total']:.2f} of ${args.cap:.2f}.")
        if r["total"] + r["estimate"] > args.cap:
            print(f"dry run: WARNING, the estimate does not fit under the cap; the real run would stop early.")
        return 0
    if r["stopped"]:
        print(f"run: STOPPED at the {r['stopped']}")
    print(f"run: {r['made']} call(s) made, {r['skipped']} already saved. Spent so far: ${r['total']:.2f} of ${args.cap:.2f}.")
    return 2 if r["stopped"] else 0


if __name__ == "__main__":
    sys.exit(main())
