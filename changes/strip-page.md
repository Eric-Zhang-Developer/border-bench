## What shipped
The page: a picker of countries, and for each one a strip of tiles (rectangle, circle, then every model, oldest first). Each tile lays the model's line over the true border, with missed land in a warm colour and invented land in blue, and the overlap % under it. Opening a tile gives a large view with every sample's score, a slider and arrow-key stepping. It reads `results/results.json` when that file exists and otherwise a committed sample, under a "sample data" banner that cannot show over real results. Light and dark, phone to desktop, keyboard only, reduced motion.

## Where it lives
`site/app/page.tsx`, `site/app/strips.tsx`, `site/app/globals.css` (the page); `site/lib/geo.ts` (one shared frame per country) and `site/lib/geo.check.mjs` (its check, run before every build); `site/lib/results.ts` (which file is read); `site/fixtures/` (the sample, and `make-stress.mjs` for `npm --prefix site run stress`); `site/screenshots/strip-page-*.png`; `specs/decisions/strip-page-display.md`.

## How to check it
verify: `python3 pipeline/verify.py` pass at 575eb84
In a browser: `npm --prefix site run dev` for the sample, `npm --prefix site run stress` for six awkward made-up countries and fifteen models.

## Gaps
No real drawing has been on the page: `results/results.json` does not exist yet, so "every model has a tile on every strip" was checked only against the stress fixture (6 strips complete). Not deployed; that is the maintainer's step, and the build needs `results/` (one folder above `site/`) to be readable where it is built. Checked in Chrome only, driven by a script; no Safari, no Firefox, no screen reader. The modern foil's source cannot be credited in the footer (issue #22). Model names show as raw ids until issue #18 is settled. A country as thin as Chile is only a few pixels wide on a tile. The build fetches two typefaces from Google Fonts once and serves them itself. The follow-up with screenshots of the six real strips waits for `full-run`.
