# NOW

Updated: 2026-11-10 by Claude (planning session with the maintainer)

## Where things stand
- The page shows real results: fourteen Claude models on six countries, drawn with the frozen prompt `prompts/p1.txt`.
  Run it with `npm --prefix site run dev`.
- Done (done note on `main`): scaffold, runner, sonnet-45-archive, truth-modern, truth-history, scorer, prompt-pilot,
  strip-page.
- `full-run` is in flight. Fourteen of fifteen models are in. Claude Opus 5 is held after one call that cost $0.73;
  the maintainer has not said how many tries it gets.
- The modern true borders are land only, from the 1:10m map, with the Great Lakes cut out
  (`specs/decisions/004-truth-is-land.md`).
- Spend: $31.40 in saved answers on `main`, plus the one Opus 5 call on its branch, of the $60 cap. Four lost calls
  are not counted (issue #31).
- Not deployed. Nothing is public but the repository.

## Next step
`head-to-head` (`specs/features/head-to-head/spec.md`), page lane, `eric-4`: a view where two models draw the same
country side by side, and a clip of the oldest model against the newest for the maintainer to post.

## Open questions
- Maintainer: tries for Claude Opus 5 (the `full-run` worker is waiting).
- Maintainer: issues #18, #22, #27, #28, #31 (`gh issue list --label needs-human`).
- Maintainer: a ship date for the `mvp` milestone. Claude Sonnet 4.5 retires on 2026-11-30.
- Maintainer: whether the pitch goes in this public repo; when to deploy.
- Raised in chat, not decided: a different country list (the lower 48 is saturated; single states and Afghanistan
  were floated). Any new country needs Claude Sonnet 4.5 collected before it retires.
- Drafts #40 and #41 (contact sheets and notes for the land-only borders) are not reviewed.

## Next milestone
`mvp`, no date yet. In: scaffold, runner, sonnet-45-archive, truth-modern, truth-history, scorer, prompt-pilot,
full-run, strip-page, head-to-head. Cut list: empty.
