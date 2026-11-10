# truth-history: Prussia comes from HistoGIS's own outline, because the "1820 file" does not exist as planned

- Date: 2026-11-09   Decided by: the maintainer (the download), agent (the rest; the maintainer reviews the pull request)   Feature: truth-history
- **Context:** the spec named "the HGIS Germany 1820 state boundaries (via HistoGIS)". Reading HistoGIS's catalogue
  showed three things the plan did not know.
  1. HistoGIS does not hand out one file per year. It keeps one outline per state for each stretch of time in which
     that state's border did not change. Its record called "German States Stateborders 1820" holds four small Saxon
     duchies and nothing else.
  2. Prussia's outline is shape 10039, which HistoGIS dates **9 June 1815 to 31 May 1834**. It covers 1 January 1816
     directly, so no 1820 map has to stand in for 1816.
  3. The outline is HistoGIS's own work, not the HGIS Germany file. HistoGIS says its shapes were "adopted from data
     provided by the Census Mosaic Project", edited, and then "compared to data provided by the HGIS Germany
     Project". Its credit line also names an 1835 map and "© OpenStreetMap contributors".
- **Options:**
  - A, use HistoGIS shape 10039. Academic work (Austrian Academy of Sciences), dated to the day, CC BY 4.0 by the
    site's imprint, and it includes the eastern provinces.
  - B, fetch the HGIS Germany file itself from the library that hosts it. A different download with a licence nobody
    has read yet, and not what the maintainer was asked about.
  - C, CShapes-Europe, a newer file from the CShapes authors that starts in 1816. Found while checking sizes; not
    downloaded; non-commercial and share-alike.
  - D, the spec's fallback, Germany 1914 from CShapes. Only for the case where the eastern provinces are missing.
    They are not missing.
- **Choice:** A. The maintainer was asked in chat with points 1 to 3 spelled out. Maintainer, 2026-11-09: "Yes,
  download it". The check the spec demands passed: 54.5% of the outline lies in today's Poland, 4.6% in today's Russia (the
  Kaliningrad region, once northern East Prussia) and 0.9% in today's Lithuania (the Memel strip).
- **Found after the download, and put to the maintainer before anything was pushed:** HistoGIS publishes the outline
  as CC BY 4.0, but the Census Mosaic files it was built from come with narrower terms: "The data provided on this
  page can be freely used for non-commercial scientific purposes, as long as you register as a user with the Mosaic
  project and the source of the data is properly cited." (https://mosaic.ipums.org/historical-gis-datafiles, read
  2026-11-09). Asked whether Prussia should go into the pull request with that flagged, or be held back.
  Maintainer, 2026-11-09: "Yes, flagged". So the outline is in, its `SOURCE.md` says to treat it as non-commercial,
  and both HistoGIS and Census Mosaic are credited. Poland 1938 is non-commercial and share-alike in any case.
- **Still not settled:** nobody has asked HistoGIS how its CC BY 4.0 label fits Census Mosaic's terms, or what the
  "© OpenStreetMap contributors" in its credit line implies (OpenStreetMap's own licence is share-alike).
- **Also found:** the outline shows the Vienna settlement as it stood by April 1817, not exactly 1 January 1816. The
  Duchy of Westphalia is already inside (handed over 15 July 1816). The list, with sources, is in
  `targets/prussia-1815/SOURCE.md`. The outline is used for 1 January 1816 anyway: that is the agent's call.
- **How to undo:** change the URL and checksum in `pipeline/prep_history.py`, run it, review the new preview. Cheap
  until Prussia's scores are public; a one-way door after.
