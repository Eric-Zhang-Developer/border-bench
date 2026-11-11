---
name: Two models draw the same country side by side, point by point, and the clip of it is worth posting
depends_on: [strip-page]
owns: [site/]
assignee: "eric-4"
---

# Head to head

Maintainer, 2026-11-10: "I want to make this really beautiful, something that you can just post on, tech twitter, and
then be like, 'Damn.'" Then: "why would we not make this generalizable?" And on the fine print: "we dont need to have
all of this or we can but in small subscript".

So this is one general view and one clip recorded from it. The clip is the point; the view is how any other pair gets
its clip for free.

## Plan
1. A page at `/duel` that replays any two models drawing any one country.
2. A recorder: one command turns that page into a video file, frame by frame.
3. The hero clip: the oldest model in the results against the newest. Render the last frame for all six countries,
   look at them, pick the one that looks best, record it.

## Requirements

**The view**
- A page at `/duel` in the static export, with three choices: country, left model, right model. It opens on Indonesia,
  the oldest model on the left and the newest on the right. The choice is kept in the query string, so a reload and
  the recorder land on the same pair. The main page links to it.
- **The stage** is a 16:9 block that scales as one piece. Everything in the clip is on the stage; the choices and the
  playback controls sit outside it. On the stage:
  - the words the models were sent (the target string), once;
  - per side: Anthropic's display name for the model, its release month, the map, a running stream of the
    coordinates being drawn, and a count of points so far;
  - the true border under both maps from the start, faint;
  - one small line at the bottom: `same prompt · at most 400 points · no tools · borderbench`. Nothing else is
    fine print on the stage.
- **The replay.** Each line grows one point at a time, in the order of the saved outline, pieces in order, with no
  line drawn between pieces. Both sides move at the same number of points per second, set so the longer drawing
  takes about 8 seconds. A side that finishes first waits.
- **The ending.** When both lines are done: missed land and invented land wash in, then the two overlap numbers
  land. No number is on screen before its drawing is finished. The last frame holds about 2.5 seconds and must work
  as a still.
- Colours, masks and scores are the strip's: the same `score`, the same drawing (the median one), the same two
  colours meaning the same two things. The two maps share one frame, fitted to the true border and these two
  drawings.
- A model with no drawing gets the strip's empty "no drawing" panel and its number. A drawing tagged "drew the
  modern country" gets the tag and the dotted modern outline at the end.
- **Names.** The results file still holds raw model ids as labels (issue #18). Every run file holds the name
  Anthropic gives the model (`model_display_name`). Show that name, on the strip too. No hand-written list of names;
  a model with no saved name shows its id.
- Controls: play or replay, pause, and a scrubber over the clip's time. Keyboard works. With reduced motion on, the
  page opens on the finished frame and plays only when asked.
- Works at phone width and in light and dark. The clip is recorded in dark.

**The recorder**
- One command, no new dependency: it drives the Chrome already on the machine and encodes with `ffmpeg`.
- It steps the view's clock frame by frame, so the same pair always gives the same frames. It records the built
  site, not the dev server.
- Output: an `.mp4` (1920 by 1080, 60 frames a second, H.264, plays in QuickTime and uploads to X) and the last
  frame as a `.png`.

**The hero**
- Oldest against newest: Claude Sonnet 4.5 and Claude Fable 5.2 as the results stand.
- Commit the hero clip, its last frame, and the last frames for the other five countries.

## Validation
- `npm --prefix site run build` -> `geo.check: ok`, and the export holds the `/duel` page beside the main one.
- `python3 pipeline/verify.py` -> `verify: ... site built; 6 strips complete`.
- In a browser at 390, 1280 and 1920 wide, light and dark: open `/duel`, pick each country, change both models,
  play, pause, scrub, replay, all with the keyboard too. Screenshots in the PR.
- Poland 1938 with Claude Haiku 5.5 on one side shows the "drew the modern country" tag and the dotted outline.
- For three pairs, the two numbers on the stage equal the same tiles' numbers on the strip.
- The recorder command, run twice on the hero pair, gives a byte-identical last frame.
- `ffprobe` on the clip -> 1920x1080, h264, yuv420p, 60 fps, under 15 seconds. Open it and watch it once.
- A check that fails if the replay order stops matching the saved outline (in `site/lib/geo.check.mjs`, which runs
  before every build).

## Defaults
- A purely visual choice is the worker's: make it, show it. The bar is the maintainer's "Damn", so spend the effort
  on type, timing and the last frame, not on options.
- Out: more than two models at once, a clip for every pair, sound, share buttons, deploying, posting. Posting is the
  maintainer's.
- The query string is not a promised link until the site is deployed.
- No score, prompt, true border or run file changes.
