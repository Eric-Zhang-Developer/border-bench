# NOW

Updated: 2026-11-09 by Claude (planning session with Eric)

## Where things stand
- `scaffold` is merged: an empty pipeline and an empty page build, test and verify. Nothing else is built.
- The prompt is tentative: three candidates in `specs/features/prompt-pilot/candidates/`, reasoning in
  `specs/decisions/001-prompt.md`.
- No model has been called and no dataset has been downloaded.

## Next step
Four lanes run in parallel (Eric, 2026-11-09: "Start all three"). Each worker takes only features assigned to it.
- `eric-1`, models: `runner`, `sonnet-45-archive`, then `prompt-pilot` and `full-run`.
- `eric-2`, data: `truth-modern`, then `truth-history`.
- `eric-3`, scorer: `scorer`, built on synthetic shapes.
- `eric-4`, page: `strip-page`, built against the sample results file.

The lanes meet at `prompt-pilot`, which needs the runner, the scorer and the Prussia border, and ends with Eric
choosing the prompt. The full run then goes in two stages: three models first (Sonnet 4.5, Haiku 5.5,
Sonnet 5.5), Eric looks at the strips, then the rest. The archive is still the urgent one: Claude Sonnet 4.5 retires on 2026-11-30.

## Open questions
- Eric: approve three downloads when asked: Natural Earth 50m countries, HGIS Germany 1820 states (via HistoGIS),
  CShapes 2.0.
- Eric: a ship date for the `mvp` milestone in `specs/milestones.toml`.
- Eric: whether the pitch goes in this public repo.
- Not verified: that the HGIS 1820 file includes Prussia's eastern provinces (`truth-history` checks first).
- Not verified: the $50 cost estimate. The runner's cap is $60.

## Next milestone
`mvp`, no date yet. In: scaffold, runner, sonnet-45-archive, truth-modern, truth-history, scorer, prompt-pilot,
full-run, strip-page. Cut list: empty.
