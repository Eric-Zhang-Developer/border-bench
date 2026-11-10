# Source: the contiguous United States (the lower 48 states) as of 1 January 2024

- **Source:** Natural Earth, Admin 0 – Countries, 1:10m, version 5.1.1. Record `United States of America` (`ADM0_A3` = `USA`).
  - File: `ne_10m_admin_0_countries.zip` from https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip
  - Checksum (SHA-256): `ce1ac7036499a0edd641fbc093cd209a98f96a49d2eca8480aaacad35138a7f6`
- **Lakes from:** Natural Earth, Lakes + Reservoirs, 1:10m, version 5.0.0.
  - File: `ne_10m_lakes.zip` from https://naciscdn.org/naturalearth/10m/physical/ne_10m_lakes.zip
  - Checksum (SHA-256): `0803a06f9c3cb4671d89b68c48b142aad9366ba40f665245e12a913fbc61722a`
- **Fetched:** 2026-11-09 (both files)
- **Licence:** public domain. Natural Earth: "All versions of Natural Earth raster + vector map data found on this website are in the public domain." https://www.naturalearthdata.com/about/terms-of-use/
- **Built by:** `uv run python -m pipeline.prep`. Nothing here is edited by hand.

## Edits
1. Kept only the pieces whose centre lies inside longitude -125.0 to -66.0, latitude 24.0 to 50.0. This removes Alaska and Hawaii. Territories (Puerto Rico, Guam and others) are separate records in the source and were never part of the shape.
2. Cut out the 16 lakes that reach the edge of the shape, as the lakes file draws them: Amistad Reservoir, Chiputneticook Lakes, Falcon Lake, Lake Champlain, Lake Erie, Lake Huron, Lake Michigan, Lake Ontario, Lake Saint Clair, Lake Superior, Lake of the Woods, North Channel, Rainy Lake, Saginaw Bay, St. Marys River, Whitefish Bay. A lake reaches the edge when the border or the coast runs through it or touches it, or when it is joined to a lake that does. This removed 158,579 km². Where a lake's outline crosses the border, the crossing point is computed; no other coordinate is new.
3. Ring order was changed to the GeoJSON convention (outlines counter-clockwise). No coordinate changed.

## What the shape includes
- 177 separate piece(s), 18670 points, no holes.
- The shape is the outline of the land (`specs/decisions/004-truth-is-land.md`). Lakes that reach the edge are cut out. Lakes that lie wholly inside stay in, because an outline cannot leave them out without a hole: 97 in the lakes file, 30,590 km² in all. Rivers are not cut out.
- Disputed areas follow Natural Earth's default (de facto) view. Nothing was added or removed for a dispute.
- The published land figure also leaves out the lakes and rivers that lie wholly inside the country, which the shape keeps. So the shape should sit a little above the land figure, and it does.

## Area check
- Area on the WGS84 ellipsoid: measured 7,783,469 km² against a published land area of 7,663,942 km²: +1.6% (and -3.7% against the published total, 8,080,464 km²).
- **Within the 2% the spec asks for.**
- Published figure from: Wikipedia, "Contiguous United States", which cites the CIA World Factbook's area listing. Read on 2026-11-09.
