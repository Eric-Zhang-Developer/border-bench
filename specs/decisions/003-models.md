# 003: Models and settings

- Date: 2026-11-09   Decided by: the maintainer and Claude   Feature: runner

## Context
Maintainer, 2026-11-09: "we would just use Anthropic's models for now", then "fuck it we use you too as well" (Claude
Fable 5.2 is in).

## Choice
- **Lineup:** every model the Models API returns for the maintainer's key, except Mythos and preview ids. The strip is ordered
  by the `created_at` the Models API reports. Expected, from a table dated 2026-10-06 (the live list wins):
  Sonnet 4.5, Haiku 4.5, Opus 4.5, Opus 4.6, Sonnet 4.6, Opus 4.7, Opus 4.8, Sonnet 5, Opus 5, Fable 5, Haiku 5.5,
  Sonnet 5.5, Opus 5.5, Fable 5.1, Fable 5.2.
- **Settings:** each model runs as it ships. No `thinking`, `effort` or sampling parameters are sent. Newer models
  think by default and several cannot have it turned off, so "as it ships" is the only setting that applies to all.
  The page says so.
- **No fallback model**, although the SDK guide recommends one for newer models. A fallback would put one model's
  drawing under another model's name.
- **Samples:** three per model and target; one for the three Fable models ($50 per million output tokens).
- **Spend:** about $50 estimated (not measured), hard cap $60 in the runner.

## Known weaknesses
- **No primitive end.** Every Claude 3 model is retired. The oldest served model is Sonnet 4.5 (September 2025), so
  the strip spans about 14 months. If the strips look flat, the fix is older or smaller models from other providers.
- **Thinking is confounded with generation.** The reason-first prompt (decision 001) shrinks this; it does not
  remove it.
- Fable 5.2's price is assumed equal to Fable 5.1's.

## How to undo
Adding a provider or a model is additive: new run files, same prompt, same scorer.
