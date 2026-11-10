---
name: True borders for the USA, Chile, Indonesia and Croatia, each with its source
depends_on: [scaffold]
owns: [pipeline/prep.py, targets/usa/, targets/chile/, targets/indonesia/, targets/croatia/]
assignee: "eric-2"
---

# Modern truth

## Plan
1. Download Natural Earth 50m countries (public domain). The maintainer approves the download in chat first.
2. `pipeline/prep.py` cuts each target out and writes its folder.
3. Render `preview.png` for each target.

## Requirements
- Each `targets/<id>/` holds:
  - `target.toml`: `id`, `name` (the exact string below), `date`.
  - `truth.geojson`: one MultiPolygon in [longitude, latitude].
  - `SOURCE.md`: the source, its version and URL, its licence, the date fetched, and every edit made.
  - `preview.png`: the truth drawn on a plain background, with a scale bar.
- Names: as in `specs/features/sonnet-45-archive/spec.md` for the four modern MVP targets.
- `usa` is the lower 48 states only: Alaska, Hawaii and territories removed.
- `chile` excludes the Antarctic claim. Islands that Natural Earth includes stay.
- No hand-drawn or adjusted coordinates. Every edit is a named, repeatable step in `prep.py`.
- The downloaded source file is not committed; `prep.py` can rebuild every target from a fresh download.

## Validation
- `uv run python -m pipeline.prep` -> rewrites the four folders with no diff.
- Each `truth.geojson` loads as a valid MultiPolygon; its area is within 2% of the country's published land area
  (cite the figure in the PR).
- The four previews are embedded in the PR. The maintainer looks at them: this path is human-reviewed.

## Defaults
Disputed slivers follow Natural Earth's default (de facto) view and are noted in `SOURCE.md`.
