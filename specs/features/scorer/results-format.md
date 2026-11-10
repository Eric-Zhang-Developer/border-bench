# The results file

`results/results.json` is the one file the page reads. `results.example.json` in this folder fixes its shape. The
example's contents are made up; only the keys and types matter.

| Field | Meaning |
|---|---|
| `schema` | 1. Raised only by a `plan:` PR. |
| `prompt.id`, `prompt.text` | The frozen prompt, shown verbatim on the page. |
| `targets[].id`, `name`, `date`, `kind` | `kind` is `modern` or `history`. `name` is the exact string sent to the model. |
| `targets[].source` | Shown in the page footer: name, licence, link. |
| `targets[].truth` | GeoJSON MultiPolygon, [longitude, latitude], simplified for display. |
| `targets[].foil` | The same for the modern foil, or `null` on modern targets. |
| `targets[].baselines[]` | Always two, in this order: `rectangle`, `circle`. Each has a `score` and an `outline`. |
| `targets[].models[]` | In release order (`released`, oldest first). The same models, in the same order, on every target. |
| `models[].scores` | Overlap % for every sample, in sample order. One to three numbers, 0 to 100, one decimal. |
| `models[].median_sample`, `score` | Index of the sample shown, and its score. With one sample: 0. |
| `models[].outline` | The shown sample's drawing as a MultiPolygon, or `null` when `no_drawing`. |
| `models[].points` | Points in the shown sample as the model wrote it. |
| `models[].flags` | `no_drawing`, `over_400_points`, `drew_modern` (history targets only; otherwise false). |

Missed and invented land are not in the file. The page works them out from `truth` and `outline`, so the picture and
the score cannot disagree about which drawing is shown.
