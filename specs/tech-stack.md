# Tech stack

New dependencies only through a `contract:` PR.

| Layer | Choice |
|---|---|
| Pipeline | Python 3.13, run with uv (pinned in `pyproject.toml` and `.python-version`: it has wheels for every dependency; exact library versions are in `uv.lock`) |
| Pipeline libraries | `anthropic`, `shapely`, `pyproj`, `numpy`, `Pillow`, `pytest` |
| Site | Next.js 16.4.6 static export, TypeScript, Tailwind 4.3.3, d3-geo drawing to SVG (d3-geo is added by `strip-page`) |
| Data / database | JSON and GeoJSON files in the repo. No database, no API routes, no auth |
| Hosting | Vercel (a one-way door: the maintainer sets it up) |
| Tests | pytest; the golden cases are in `specs/features/scorer/spec.md` |

Model calls use the official `anthropic` SDK with streaming, `max_tokens` 64000, and no other parameters. The key is
`ANTHROPIC_API_KEY` in `.env`, which is gitignored.

## Layout
```
prompts/               frozen prompts, one file per id (p1.txt). Never edited once merged. Human-reviewed.
targets/<id>/          target.toml, truth.geojson, foil.geojson (history only), preview.png, SOURCE.md. Human-reviewed.
pipeline/prep.py       builds the modern targets from Natural Earth
pipeline/prep_history.py   builds the history targets
pipeline/run.py        calls models, writes raw answers, enforces the dollar cap
pipeline/parse.py      model answer -> rings of [lon, lat]
pipeline/score.py      overlap %, baselines, results.json
pipeline/sheet.py      contact sheet: a PNG grid of drawings over truth, for pull requests
runs/pilot/            raw answers from the prompt pilot
runs/archive/          raw answers from models about to retire
runs/p1/               raw answers for the published strips
results/results.json   the one file the site reads
sheets/                contact sheets linked from pull requests
site/                  the Next.js app
specs/, changes/, NOW.md, AGENTS.md, .agents/, .github/    the working rules (frozen: AGENTS.md, .agents/, .github/)
```

A run file is `runs/<set>/<prompt-id>/<model>/<target>/<n>.json`. It holds the prompt id, the full prompt text, the
model id and its release date, the target name, the raw answer, the stop reason, token usage and the dollar cost.

## Checks (run before marking a PR ready)
```bash
python3 .agents/scripts/check_ownership.py --lint-specs
python3 .agents/scripts/check_ownership.py --title "<PR title>" --base origin/main
python3 .agents/scripts/check_gates.py --title "<PR title>" --base origin/main
python3 .agents/scripts/check_markers.py --base origin/main
uv run pytest                      # once the scaffold feature has merged
npm --prefix site run build        # once the scaffold feature has merged
```

## Verify (see your change running)
`[verify].command` in `.agents/config.toml` is `python3 pipeline/verify.py`: it rebuilds `results/results.json` from
the committed runs with no API call (once `pipeline/score.py` exists), builds the site, and fails if a strip is
missing a tile. Its last line says which of those steps ran. It expects `results.json` to hold a `targets` list, each
target with an `id` and a `models` list whose entries have an `id`.
