# NOW

Updated: 2026-11-09 by Claude (planning session with Eric)

## Where things stand
- Nothing is built. The repo holds the working rules, the mission, three decisions and nine feature specs.
- The prompt is tentative: three candidates in `specs/features/prompt-pilot/candidates/`, reasoning in
  `specs/decisions/001-prompt.md`.
- No model has been called and no dataset has been downloaded.

## Next step
`scaffold`, then `runner`, then `sonnet-45-archive`. The archive is the urgent one: Claude Sonnet 4.5 retires on
2026-11-30 and is the first tile of every strip.

## Open questions
- Eric: `ANTHROPIC_API_KEY` in `.env` (needed from `runner` on).
- Eric: approve three downloads when asked: Natural Earth 50m countries, HGIS Germany 1820 states (via HistoGIS),
  CShapes 2.0.
- Eric: a ship date for the `mvp` milestone in `specs/milestones.toml`.
- Eric: whether the pitch goes in this public repo.
- Not verified: that the HGIS 1820 file includes Prussia's eastern provinces (`truth-history` checks first).
- Not verified: the $50 cost estimate. The runner's cap is $60.

## Next milestone
`mvp`, no date yet. In: scaffold, runner, sonnet-45-archive, truth-modern, truth-history, scorer, prompt-pilot,
full-run, strip-page. Cut list: empty.
