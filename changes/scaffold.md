## What shipped
An empty pipeline (Python 3.13 under uv) and an empty one-page site (Next.js 16.4.6 static export, Tailwind 4.3.3). CI now runs the tests and the site build on every pull request, and the verify command exists.

## Where it lives
`pyproject.toml`, `uv.lock`, `.python-version`, `pipeline/`, `site/`, `.github/workflows/ci.yml`, `.agents/config.toml` (`[verify].command`), `specs/tech-stack.md` (versions).

## How to check it
verify: `python3 pipeline/verify.py` pass at f99f96f

## Gaps
The verify command only builds the site for now: there is no scorer and no `results.json`, and its last line says so. The page has no favicon and no design; `strip-page` does both. Nothing was checked in a browser beyond one screenshot.
