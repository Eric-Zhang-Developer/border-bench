# Findings

What was checked on the web on 2026-11-09, and what was not. Each line is a search result or a page read, not a
deep review. Verify before citing in the paper.

## Related work
- **GPT4GEO** (Roberts et al., NeurIPS 2023). Asked GPT-4 for "approximately 50 points arranged clockwise" for
  Australia and the continental USA. Qualitative only, one model, no history. The closest prior work.
  https://ar5iv.labs.arxiv.org/html/2306.00020
- **"How Does A Blind Model See The Earth?"** (Henry Bass, 2025). Land or water at each coordinate. The format we
  borrow. https://www.lesswrong.com/posts/xwdRzJxyqFqgXTWbH/how-does-a-blind-model-see-the-earth
- **HiST-LLM** (NeurIPS 2024). Text multiple-choice history benchmark built on Seshat.
  https://nips.cc/virtual/2024/poster/97439
- **"Benchmarking as Source Criticism"** (2026). A critique of history benchmarks.
  https://openhumanitiesdata.metajnl.com/articles/10.5334/johd.489
- **Plan2Map** (2026). Scores model-written GeoJSON by overlap, but from documents, not memory.
  https://arxiv.org/pdf/2606.02747
- **Human draw-from-memory games** score sketches by overlap and could template a human baseline.
  https://countrydraw.org/ · https://drawcountrygame.com/
- Three searches found **no benchmark that scores model-drawn borders, modern or historical, against the truth.**
  That is not an exhaustive search.

## Data sources
| Source | Covers | Licence as found | Use |
|---|---|---|---|
| Natural Earth | Modern countries; country "point of view" variants since v5 | Public domain | Modern truth, foils |
| HGIS Germany, via HistoGIS | German states as of 31 Dec 1820 | CC BY 4.0 on HistoGIS | Prussia. Not verified: eastern provinces included |
| CShapes 2.0 | States and colonies, 1886 to 2019 | CC BY-NC or BY-NC-SA (records disagree; read the file's own licence) | Poland 1938; a larger history tier later |
| AWMC geodata | Roman Empire extent, 117 AD | CC BY-NC as found | Rome, later. Confirm the file exists in the repo |
| historical-basemaps | World snapshots incl. years 100, 200, 1400, 1492 | GPL-3.0 | **Not for scoring.** Its notes say to verify before academic use |
| Shepherd, Historical Atlas (1911) | "Central Europe about 1477", pp. 86-87 | Public domain in the US (1911) | Tracing source for the Holy Roman Empire, later |

Links: https://www.naturalearthdata.com/ · https://histogis.acdh.oeaw.ac.at/about ·
https://www.research-collection.ethz.ch/handle/20.500.11850/487987 · https://awmc.unc.edu/gis-data/ ·
https://github.com/aourednik/historical-basemaps · https://maps.lib.utexas.edu/maps/historical/history_shepherd_1911.html

## Models
- From a model table dated 2026-10-06: every Claude 3 model is retired; Claude Sonnet 4.5 retires 2026-11-30; the
  oldest models still served are Sonnet 4.5, Haiku 4.5 and Opus 4.5.
- Not verified: which older models other providers still serve.

## No open data found for
- The Holy Roman Empire's states in 1444. The date comes from a game; no public-domain atlas plate shows that year.
