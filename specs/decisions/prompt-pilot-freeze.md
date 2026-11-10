# prompt-pilot: candidate C is frozen as prompt p1

- Date: 2026-11-09   Decided by: the maintainer   Feature: prompt-pilot
- **Context:** every score depends on the prompt, and a prompt can never be changed once models have been run with it.
  Three candidates existed (`specs/decisions/001-prompt.md`): A, one line; B, explicit rules and "answer only"; C,
  explicit rules and "you may reason first". Maintainer, 2026-11-09, after seeing the numbers below: "prompt c is the
  best?", then "let's do that".
- **Options:** freeze C now on the evidence in hand / run the planned 36-call pilot on two more models first / write a
  fourth candidate.
- **Choice:** freeze C now.

## The evidence
Claude Sonnet 4.5, three tries per cell, overlap %, the middle try shown (pull request 29):

| Country | A | B | C |
|---|---|---|---|
| United States | 69.2 | 36.6 | 94.5 |
| Indonesia | 14.1 | 4.8 | 33.2 |
| Croatia | 23.3 | 20.0 | 44.5 |
| Chile | 39.0 | 30.3 | 31.3 |

Answers read only in part because their brackets are broken, out of 33 answers per candidate across all eleven
archived targets: A 0, B 7, C 1.

Among the 36 scored drawings (12 per candidate), drawings over the 400-point limit: A 5, B 5, C 1. All four runaway
drawings (935 to 3,756 points) came from B.

Claude Fable 5.2 under C, one try each (pull request 32): United States 97.1, Chile 86.1, Indonesia 89.1, Croatia 92.3.

## What this does not show
- It is one model for the comparison. Sonnet 4.5 does not think unless the prompt lets it, which is the case C was
  written for. No model that thinks by default has been run under A or B, so "C beats B" is unproven there.
- Three tries per cell is thin. Chile goes to A, and with scores this noisy that could be chance.
- C is the best of these three, not the best possible wording.
- These scores use the true borders as they stood on 2026-11-09, before the lakes question (issue 14) is settled.
  That changes the numbers a little for every candidate alike; it does not change the ranking argument.

## Why freeze anyway
The gap is large on the model that needs the prompt most, the failure counts point the same way, and Claude Sonnet 4.5
retires on 2026-11-30: the prompt has to be fixed before then, and its drawings under the frozen prompt collected.

- **How to undo:** it cannot be undone for models already retired. For the rest: add `prompts/p2.txt` and rerun every
  model still served; drawings under `p1` stay and are labelled as such.
