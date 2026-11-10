# 000: Project-wide defaults

Agents read this after their feature spec's Defaults. Humans review it first after a run. Each row says how to
undo it.

| # | Topic | Default | Undo |
|---|---|---|---|
| D1 | Anything shown on the page | No number without its picture | Remove the element |
| D2 | A source that turns out unusable | Stop and file `needs-human`; never patch a border from a second source | Close the issue |
| D3 | A choice that is purely visual | Make it and show it in the PR | Revert the PR |
| D4 | A model answer that is odd but parseable | Score it as drawn; flag it; never repair | n/a |
| D5 | Spend near the cap | Stop, commit what exists, file `needs-human`; never raise the cap | The maintainer raises it |

## When nothing covers it
1. Keep every rule in `mission.md` exact.
2. Show "unknown / needs review" rather than guess.
3. Take the smaller change that someone else can undo.
4. Prefer deterministic code over a model call, and a model call over manual guessing.
5. Log it in `decisions/<feature>-<topic>.md`.
