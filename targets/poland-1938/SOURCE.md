# Source: Poland as of 1 January 1938

- **Source:** CShapes 2.0 (Schvitz, Rüegger, Girardin, Cederman, Weidmann and Gleditsch, ETH Zurich). The one record for Poland (number 290 in the Gleditsch and Ward list of states) whose dates contain 1 January 1938: valid **1921-03-18 to 1945-05-07**.
- **File:** `CShapes-2.0.geojson` from https://icr.ethz.ch/data/cshapes/CShapes-2.0.geojson (download page: https://icr.ethz.ch/data/cshapes/)
- **Checksum (SHA-256):** `384b1ea90b9419f30a858d7ec237c85a22c60d1b35b5f85f215a1204f9989d42`
- **Fetched:** 2026-11-09
- **Licence:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0). In plain words: you may copy and change this outline **only for non-commercial use**, you must credit the authors, and anything you build from it and share **must carry this same licence**. The MIT licence on this repo's code does not apply to this folder.
- **Where the licence is stated.** Only on the download page: "CShapes by Schvitz, Rüegger, Girardin, Cederman, Weidmann, Gleditsch is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License." The data file carries no licence text. The "codebook" offered beside it is an instruction sheet for the project's coders and has none either. The library record that some catalogues point to (https://doi.org/10.3929/ethz-b-000487987) is the journal article about the dataset, licensed CC BY-NC 4.0 without the share-alike part, which is probably why catalogues disagree. **Judgment call:** the download page speaks for the data, and it is also the stricter of the two.
- **Credit, as the authors ask for it:** Schvitz, Guy, Seraina Rüegger, Luc Girardin, Lars-Erik Cederman, Nils Weidmann, and Kristian Skrede Gleditsch. 2022. "Mapping The International System, 1886-2017: The CShapes 2.0 Dataset." Journal of Conflict Resolution 66(1): 144–61.
- **Built by:** `uv run python -m pipeline.prep_history`. Nothing here is edited by hand.

## Edits
1. The source stores this border as a single Polygon. It was wrapped, unchanged, as a MultiPolygon with one piece, the form every target uses.
2. Ring order was changed to the GeoJSON convention (outlines counter-clockwise). No coordinate changed.

## What the shape includes
- 1 separate piece(s), 0 hole(s), 888 points, 388,378 km² on the WGS84 ellipsoid. CShapes lists the area as 388,378 km².
- Where its land lies on today's map (Natural Earth 1:50m borders):
  - Poland: 208,694 km² (53.7%)
  - Ukraine: 89,120 km² (22.9%)
  - Belarus: 81,151 km² (20.9%)
  - Lithuania: 9,268 km² (2.4%)
  - Everything else: 144 km² (0.0%). This is sea between the two maps' coastlines and thin slivers along borders, because the two maps were not drawn from the same survey.
- 53.7% of it lies inside today's Poland, the foil. Its easternmost point is at 28.40°E; today's Poland ends at 24.11°E.
- **Published area:** "388 634 km² (1 stycznia 1938 r.)" https://pl.wikipedia.org/wiki/II_Rzeczpospolita The shape measures -0.07% against it.
- **One outline for 24 years.** CShapes uses this outline for the whole of 1921-03-18 to 1945-05-07. Its coding rules leave out any change smaller than 10,000 km² and wartime changes that were later undone (its codebook, page 4). So the land Poland took from Czechoslovakia after the target date ("po zajęciu Zaolzia w październiku 1938 r.", same page as the area) is not in the dataset at all, and no change of that size falls before 1 January 1938 that the outline would be missing by those rules.
- **It is coarse.** The whole border is 888 points. Compare the Prussia outline, which has about seven times as many for a smaller country.
- Spot checks, repeated on every build. Positions are approximate, typed by hand, and only ever answer "inside or outside?".
  - Danzig (54.35°N, 18.65°E): **outside**. The Free City of Danzig was not part of Poland; CShapes has it as its own record. It "remained distinct from both the post-war Weimar Republic and the newly independent Polish Republic". https://en.wikipedia.org/wiki/Free_City_of_Danzig
  - Gdynia (54.52°N, 18.53°E): **inside**. Poland's strip of Baltic coast.
  - Wilno (Vilnius) (54.69°N, 25.28°E): **inside**. Today in Lithuania.
  - Lwów (Lviv) (49.84°N, 24.03°E): **inside**. Today in Ukraine.

## The foil (`foil.geojson`)
The modern country a model might draw instead of the historical one. It is never scored as truth.
- **Source:** Natural Earth, Admin 0 – Countries, 1:50m, version 5.1.1. Record `Poland` (`ADM0_A3` = `POL`).
- **File:** `ne_50m_admin_0_countries.zip` from https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip
- **Checksum (SHA-256):** `5fed433373581fa648920435f937d95f2d3c0200e067409c6478dcdf1b853139`
- **Fetched:** 2026-11-09
- **Licence:** public domain. Natural Earth: "All versions of Natural Earth raster + vector map data found on this website are in the public domain." https://www.naturalearthdata.com/about/terms-of-use/
- **Edits:** ring order changed to the GeoJSON convention. No coordinate changed.
