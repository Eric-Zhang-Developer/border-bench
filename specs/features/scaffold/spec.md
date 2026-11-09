---
name: An empty pipeline and site that build, test and verify
depends_on: []
owns: []
assignee: ""
bootstrap: true
---

# Scaffold

## Plan
1. `pyproject.toml` for uv, pinned to a Python version with wheels for every library in `specs/tech-stack.md`.
2. `pipeline/` as a package with one passing placeholder test.
3. `site/`: Next.js static export, TypeScript, Tailwind, one page that says the project is in progress.
4. Add `uv run pytest` and `npm --prefix site run build` to the CI "Project checks" step.
5. Set `[verify].command` in `.agents/config.toml`.
6. Extend `.gitignore` (`.venv/`, `node_modules/`, `.next/`, `site/out/`).

## Requirements
- `uv sync && uv run pytest` passes on a fresh clone.
- `npm --prefix site ci && npm --prefix site run build` produces a static `site/out/`.
- No model call, no download, no API key needed.
- The verify command rebuilds `results/results.json` from committed runs when `pipeline/score.py` exists, builds the
  site, and fails if any strip in `results.json` is missing a tile. Until the scorer exists it only builds the site
  and says so in its last line.

## Validation
- `uv run pytest` -> `1 passed`.
- `npm --prefix site run build` -> exit 0 and `site/out/index.html` exists.
- `python3 .agents/scripts/verify.py --slug scaffold --worktree .` -> prints a `verify:` line.
- CI is green on the PR with the two project checks running.

## Defaults
Latest stable versions of Next.js and Tailwind at the time of the PR; record them in `specs/tech-stack.md`.
