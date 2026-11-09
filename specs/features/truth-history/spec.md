---
name: True borders for Prussia in 1816 and Poland in 1938, each with a modern foil
depends_on: [truth-modern]
owns: [pipeline/prep_history.py, targets/prussia-1815/, targets/poland-1938/]
assignee: ""
---

# History truth

## Plan
1. Eric approves two downloads in chat: the HGIS Germany 1820 state boundaries (via HistoGIS) and CShapes 2.0.
2. `pipeline/prep_history.py` builds both targets and their foils.
3. Render previews with the foil outlined over the truth.

## Requirements
- Same folder contents as `truth-modern`, plus `foil.geojson`: modern Germany for Prussia, modern Poland for Poland
  1938, both from Natural Earth.
- Names: "the Kingdom of Prussia as of 1 January 1816" and "Poland as of 1 January 1938".
- **Prussia:** the truth is the Kingdom of Prussia in the 1820 file, including the provinces outside the German
  Confederation (East Prussia, West Prussia, Posen). `SOURCE.md` lists any border change between 1816 and 1820 that
  the file reflects, with a citation, or says none was found and what was checked.
- **If the 1820 file does not include those eastern provinces, stop.** Do not patch it from another source. File a
  `needs-human` issue proposing Germany 1914 from CShapes as the replacement.
- **Poland:** the CShapes polygon valid on 1 January 1938.
- `SOURCE.md` states each licence. CShapes is non-commercial and share-alike; say so in plain words.

## Validation
- `uv run python -m pipeline.prep_history` -> rewrites both folders with no diff.
- Prussia's truth has at least two separate pieces. Poland 1938's truth extends east of modern Poland's eastern
  border.
- Both previews are embedded in the PR beside a public-domain reference map of the same date (link it). Eric looks at
  them: this path is human-reviewed.

## Defaults
Enclaves inside Prussia stay as holes if the source has them.
