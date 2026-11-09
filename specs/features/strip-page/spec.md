---
name: One page where a stranger can see whether the models got better
depends_on: [scaffold]
owns: [site/]
assignee: "eric-4"
---

# Strip page

## Plan
1. Load `results/results.json` at build time if it exists; otherwise load `site/fixtures/results.json`, a copy of
   `specs/features/scorer/results.example.json`, and show a visible "sample data" banner.
2. Build the strip, the tile, the big view and the scrubber.
3. Design pass, then deploy preview.

## Requirements
- Built against the sample file, in parallel with the scorer and the model runs. The page must render any file
  with the shape of `specs/features/scorer/results.example.json`, for any number of targets and models.
- The "sample data" banner can never appear when `results/results.json` exists.
- **Target picker**: six targets.
- **Strip**: rectangle, circle, then one tile per model in release order.
- **Tile**: truth as a filled shape, drawing as an outline, missed land in one colour and invented land in another;
  under it the model name, release month and overlap %. A failed drawing is an empty tile labelled "no drawing". A
  history tile may carry the tag "drew the modern country".
- **Big view**: selecting a tile enlarges it and shows all three sample scores; left and right arrow keys step
  through the strip.
- **Scrubber**: a slider under the big view steps through models in release order.
- **Header**: "We asked each model to draw this from memory", the sentence "each model ran with its default
  settings", and the full prompt verbatim one click away.
- **Footer**: data sources with their licences, and a link to the repo.
- Maps are d3-geo to SVG, in an equal-area projection centred on the target. No tile basemap.
- Works at phone width, in light and dark, and with the keyboard alone. Honors reduced motion.
- No number appears without the drawing it describes.

## Validation
- `npm --prefix site run build` -> static export, no network request at runtime.
- In a browser at 390, 1280 and 1920 wide, light and dark: pick each target, open a tile, step with the arrow keys,
  drag the scrubber. Screenshots in the PR.
- Every model in `results.json` has a tile on every strip (the verify command checks this).
- Deploying to Vercel is Eric's step; the PR ends at a local build and screenshots.

## Follow-up, once `full-run` is on main
A `fix(strip-page)` PR by the same worker: screenshots of all six real strips, and any fix the real drawings call
for (very small islands, a drawing far outside the frame, a failed drawing).

## Defaults
Polygon morphing, share images and a leaderboard table are out. If a choice is purely visual, make it and show it.
