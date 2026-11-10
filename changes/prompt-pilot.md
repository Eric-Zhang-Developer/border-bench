## What shipped
The prompt is frozen: `prompts/p1.txt` is candidate C, the one that lets a model reason before it draws. The maintainer chose it on 2026-11-09 from 36 scored drawings by Claude Sonnet 4.5 under all three candidates and a first look at Claude Fable 5.2 under C. The separate 36-call pilot that was planned was not run.

## Where it lives
`prompts/p1.txt`, `specs/decisions/prompt-pilot-freeze.md` (the numbers and what they do not show), `specs/features/prompt-pilot/candidates/` (the three texts), `sheets/pilot/` (the first look), `specs/features/scorer/archive-*.png` (the comparison).

## How to check it
not verified by `verify.py`: this change adds a text file and no behaviour. `cmp prompts/p1.txt specs/features/prompt-pilot/candidates/c.txt` prints nothing.

## Gaps
The comparison is one model, three tries per cell. No model that thinks by default was run under candidates A or B. Chile scored higher under A. The scores behind the choice predate the lakes question (issue 14). No drawing has been made under the id `p1` yet; that is the full run.
