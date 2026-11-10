# How we write pull requests

A pull request here is the paper trail for a decision. Its readers are the maintainer, the next agent, and one day a professor
or a reviewer of the paper. Most of them will not read the code. They need to know **why** something was done, what
was turned down, and what is true now.

Maintainer, 2026-11-09: "It shouldn't be too technical, and it should reason more about the why than the what, but also
the what."

## The title
`type(slug): a plain sentence saying what is now true`

- The prefix is for the checks (`feat`, `fix`, `docs`, `plan`, `contract`; see `AGENTS.md`).
- The sentence is for people. Someone who does not program should understand it when it is read aloud.
- No file names, function names or library names in the title.

Good: `feat(truth-history): Prussia's 1816 border, in two pieces, from the German historical atlas data`
Bad: `feat(truth-history): add prep_history.py and geojson files`

## The body, in this order

### In plain words
Two or three sentences. What is different now, for someone who has never seen the code.

### Why
The main section, and usually the longest.
- **The question** that forced a choice.
- **What we chose**, and the reason in a sentence or two.
- **What we turned down**, and why. Name at least one real alternative.
- **Who decided.** Quote the maintainer with the date when the call was theirs. Otherwise say it was the agent's call and link the
  decision file.

### What changed
A short list. Each line says the change in plain words first, then the path in backticks.

### See it
The picture. Required whenever the pull request changes a drawing, a score, a true border, a prompt or the page.
- Truth: `targets/<id>/preview.png`, beside a reference map.
- Drawings and scores: a contact sheet from `pipeline/sheet.py`.
- The page: screenshots.

Put one sentence under each picture saying what to look at. Commit the image and embed it by its raw URL at the pull
request's latest commit, because relative paths do not render in pull request text.

### Does any score change?
Answer on every pull request. This is a benchmark: a silent change to a score is the worst kind of bug.
- "No." is a complete answer.
- "Yes" comes with a before and after table and the reason. If the score is already public, the change is a one-way
  door and waits for the maintainer.

### Sources
Required whenever data or a historical fact enters the repo. For each source: the link, the licence, what was taken,
and every edit made. List judgment calls as judgment calls ("the 1820 file is used for 1816; no border change found
in between; checked: ...").

### Cost
Required whenever models were called: number of calls, dollars spent, and the running total against the cap.

### Checks
The command and the last lines it printed. A fix shows the failing line before and the passing line after.

### Not done, not sure
What was skipped, what was not verified, what is unknown. "Merged" is not "checked by a person".

## Writing rules
1. **Write for a curious reader who does not program.** A history professor should follow the first three sections
   without a glossary.
2. **Why before what.** If the Why section is shorter than What changed, it is probably missing the alternative.
3. **Explain a term the first time, or replace it.** "Overlap % (the shared area divided by the area either shape
   covers)", not "IoU".
4. **Numbers carry a unit and a source.**
5. **Code names stay in What changed and Checks.**
6. **Say what is true now.** Not "improved the parser" but "an answer with two JSON blocks is now read from the last
   one".
7. **One decision per pull request** where possible.
8. **Short sentences.** No abbreviations a newcomer would have to look up.
9. **Say "the maintainer", never a personal name.** Quote a decision as `Maintainer, <date>: "..."`.

Commit messages follow the same spirit: the subject says what is now true, the body says why and what the
alternative was. No co-author trailers and no "generated with" footers.

## A short example

> **feat(truth-history): Prussia's 1816 border, in two pieces, from the German historical atlas data**
>
> **In plain words.** The benchmark now has a true border for the Kingdom of Prussia in 1816 to score drawings
> against, and a modern Germany outline to catch models that draw the wrong century.
>
> **Why.** We needed a border a historian would accept. We chose the HGIS Germany project's 1820 boundaries because
> they are academic work with a clear licence. We turned down the historical-basemaps project: its own notes say to
> verify it before academic use. The 1820 file stands in for 1816; we found no border change in between (checked: ...).
>
> **See it.** *(preview image)* Look for the gap between the western provinces and the rest: Prussia was two pieces.
>
> **Does any score change?** No. Nothing was scored against Prussia before.
>
> **Sources.** HGIS Germany via HistoGIS, CC BY 4.0, state boundaries of 31 December 1820. Edits: kept the Kingdom of
> Prussia only; merged its provinces into one shape.
>
> **Not done, not sure.** Enclaves smaller than the grid cell are not visible in the preview.
