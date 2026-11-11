## What shipped
A page at `/duel` where any two models draw any one country side by side: the words they were sent, then both lines growing point by point with the numbers each model wrote streaming under its map, then the strip's two colours and the two overlap numbers. Country and both models are choices kept in the address; play, pause and a scrubber work by keyboard. One command records it frame by frame. The hero clip is Indonesia, Claude Sonnet 4.5 against Claude Fable 5.2 (14.4 s, 1920 by 1080, 60 frames a second, H.264, 2.7 MB). The strip and this page now show the names Anthropic gives the models.

## Where it lives
`site/app/duel/` (the page and the stage); `site/lib/answer.ts` (the points a model wrote, from its saved answer); `site/lib/geo.ts` (`chart`, the shared frame); `site/lib/geo.check.mjs` (fails the build if a replay is not its scored drawing); `site/scripts/record.mjs` (`npm --prefix site run record`); `site/clips/indonesia.mp4` and `site/clips/indonesia.png` (the clip and its last frame); `site/clips/<country>.png` (the other five last frames); `site/screenshots/head-to-head-page-*.png`; `specs/decisions/head-to-head-replay.md`.

## How to check it
verify: `python3 pipeline/verify.py` pass at a0617d3
In a browser: `npm --prefix site run dev`, then `/duel`. A new clip: `npm --prefix site run build && npm --prefix site run record -- --target croatia`.

## Gaps
Nobody has watched the clip as a moving picture: it was checked as frames, by `ffprobe`, by Chrome playing it and by macOS making a thumbnail of it. Not opened in QuickTime, not uploaded to X. The page was checked in Chrome only, driven by a script; no Safari, no Firefox, no screen reader, no person. At phone width the stage is small, as one scaled piece: the maps and the two numbers read, the stream of coordinates does not. The numbers on the stage carry no word saying what they measure, as the spec asks: the one small line is the only fine print. The reader of saved answers is a second copy of the scorer's rule; the build check is what keeps the two in step. Not posted, not deployed: both are the maintainer's.
