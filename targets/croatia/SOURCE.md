# Source: Croatia as of 1 January 2024

- **Source:** Natural Earth, Admin 0 – Countries, 1:10m, version 5.1.1. Record `Croatia` (`ADM0_A3` = `HRV`).
  - File: `ne_10m_admin_0_countries.zip` from https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip
  - Checksum (SHA-256): `ce1ac7036499a0edd641fbc093cd209a98f96a49d2eca8480aaacad35138a7f6`
- **Lakes from:** Natural Earth, Lakes + Reservoirs, 1:10m, version 5.0.0.
  - File: `ne_10m_lakes.zip` from https://naciscdn.org/naturalearth/10m/physical/ne_10m_lakes.zip
  - Checksum (SHA-256): `0803a06f9c3cb4671d89b68c48b142aad9366ba40f665245e12a913fbc61722a`
- **Fetched:** 2026-11-09 (both files)
- **Licence:** public domain. Natural Earth: "All versions of Natural Earth raster + vector map data found on this website are in the public domain." https://www.naturalearthdata.com/about/terms-of-use/
- **Built by:** `uv run python -m pipeline.prep`. Nothing here is edited by hand.

## Edits
1. Looked for lakes that reach the edge of the shape (the border or the coast runs through or touches them). The lakes file has none here, so nothing was cut.
2. Ring order was changed to the GeoJSON convention (outlines counter-clockwise). No coordinate changed.

## What the shape includes
- 25 separate piece(s), 2341 points, no holes.
- The shape is the outline of the land (`specs/decisions/004-truth-is-land.md`). Lakes that reach the edge are cut out. Lakes that lie wholly inside stay in, because an outline cannot leave them out without a hole: 0 in the lakes file, 0 km² in all. Rivers are not cut out.
- Disputed areas follow Natural Earth's default (de facto) view. Nothing was added or removed for a dispute.
- At 1:10 million the mainland is two pieces, cut by the strip of Bosnian coast at Neum, and 23 islands are kept (Wikipedia counts 1,246 islands and islets). No lake in the lakes file lies in Croatia, so nothing was cut.

## Area check
- Area on the WGS84 ellipsoid: measured 55,023 km² against a published land area of 55,960 km²: -1.7% (and -2.8% against the published total, 56,594 km²).
- **Within the 2% the spec asks for.**
- Published figure from: land: the World Bank, "Land area (sq. km)" for Croatia, 2023 (indicator AG.LND.TOTL.K2, which takes it from the FAO), https://api.worldbank.org/v2/country/HRV/indicator/AG.LND.TOTL.K2. Total: Wikipedia, "Geography of Croatia", which cites Croatia's Statistical Yearbook 2011. Read on 2026-11-09.
