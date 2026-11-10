# Source: the Kingdom of Prussia as of 1 January 1816

- **Source:** HistoGIS, Austrian Academy of Sciences (Austrian Centre for Digital Humanities and Cultural Heritage). Shape 10039: `Preußen`, type `Kingdom`, which HistoGIS dates **1815-06-09 to 1834-05-31**. HistoGIS files it under its record "German States Stateborders 1830".
- **File:** `10039.json` from https://histogis.acdh.oeaw.ac.at/api/tempspatial/10039.json (permanent link to the same shape: https://histogis.acdh.oeaw.ac.at/shapes/permalink/4052e0f206241cc152c6e867033a9db3/)
- **Checksum (SHA-256):** `412793a97504b92580657b51d6766c08b1a446cf14f7ff648c64e2c88e7f86f7`
- **Fetched:** 2026-11-09
- **Licence, as published:** Creative Commons Attribution 4.0 (CC BY 4.0), which by itself would let anyone copy, change and publish the outline, also commercially, with credit. The HistoGIS imprint: "This website and its content is, unless indicated otherwise, licensed under a creative commons CC-BY 4.0 International licence (Attribution)." https://histogis.acdh.oeaw.ac.at/imprint The shape's own record states no other licence.
- **Licence, upstream: treat this outline as non-commercial.** HistoGIS built it from Census Mosaic files, and the Mosaic project's terms are narrower: "The data provided on this page can be freely used for non-commercial scientific purposes, as long as you register as a user with the Mosaic project and the source of the data is properly cited." https://mosaic.ipums.org/historical-gis-datafiles (read 2026-11-09). HistoGIS does not say how the two fit together. Until someone asks HistoGIS, this repo credits both and makes no commercial use of the outline. Maintainer, 2026-11-09, asked whether to include it with this flagged: "Yes, flagged".
- **Credit, as HistoGIS asks for it:** Antonia Dückelmann / Peter Paul Marckhgott-Sanabria, "German Confederation State Borders 1830", based on Census Mosaic: German Union, 1830; Woldan: Floder, Oesterreich, 1835; Census Mosaic: Europe Main, 1900 and © OpenStreetMap contributors published by Histogis.
- **Built by:** `uv run python -m pipeline.prep_history`. Nothing here is edited by hand.

## What this source is, and is not
The plan called this "the HGIS Germany 1820 state boundaries". It is not quite that, in three ways.
- **There is no 1820 file to take Prussia from.** HistoGIS keeps one outline per state for each stretch of time in which that state's border did not change. Its record named "German States Stateborders 1820" holds four small Saxon duchies and nothing else. Prussia's outline is this one, and its dates cover 1 January 1816 directly, so no later map stands in for 1816.
- **The outline is HistoGIS's own work, not the HGIS Germany file.** HistoGIS describes it: "Geometries of the features in the data sets (the administrative units) were adopted from data provided by the Census Mosaic Project, http://www.censusmosaic.org/. A stateborders data set was created by merging the features provided, editing them where necessary (using additional spatial data) and adding attribute information, such as state name and administrative type. Attributes of the features were then compared to data provided by the HGIS Germany Project". The HGIS Germany file itself was not downloaded and not compared.
- **The licence upstream is stricter than the licence on the label.** See "Licence" above. The credit line also names "© OpenStreetMap contributors", whose own licence (the Open Database Licence) is share-alike; HistoGIS says nothing more about that.

**Judgment calls:** HistoGIS's outline and its dates are taken as published, and the outline is treated as non-commercial. See `specs/decisions/truth-history-prussia-source.md`.

## Edits
1. Ring order was changed to the GeoJSON convention (outlines counter-clockwise). No coordinate changed.

Nothing else. No piece was dropped, no hole was filled, no point was moved, added or removed.

## What the shape includes
- 31 separate piece(s), 16 hole(s), 6137 points, 275,463 km² on the WGS84 ellipsoid. HistoGIS lists the area as 275,463 km².
- Enclaves (other states' land wholly inside Prussia, such as the Anhalt duchies) are holes, as in the source.
- Where its land lies on today's map (Natural Earth 1:50m borders):
  - Poland: 150,164 km² (54.5%)
  - Germany: 108,227 km² (39.3%)
  - Russia: 12,619 km² (4.6%)
  - Lithuania: 2,515 km² (0.9%)
  - Everything else: 1,938 km² (0.7%). This is sea between the two maps' coastlines and thin slivers along borders, because the two maps were not drawn from the same survey.
- Only 39.3% of it lies inside today's Germany, the foil.

## The check the spec asks for first: are the eastern provinces in?
Yes. East Prussia, West Prussia and Posen lay outside the German Confederation, so a map of "the German states" could
have left them out. This outline has them: the build stops unless more than 1,000 km² of the shape lies in each of
today's Poland, Russia (the Kaliningrad region, once northern East Prussia) and Lithuania (the Memel strip).

Spot checks, repeated on every build. Town positions are approximate, typed by hand to two decimals, and used only
to ask "inside or outside?". None of them is written into a border.
- Königsberg (54.71°N, 20.51°E): **inside**. East Prussia.
- Danzig (54.35°N, 18.65°E): **inside**. West Prussia.
- Posen (52.41°N, 16.93°E): **inside**. The province of Posen.
- Greifswald (54.09°N, 13.38°E): **inside**. Swedish Pomerania, handed to Prussia before the target date: "Die Übergabe an Preußen erfolgte am 23. Oktober 1815." https://de.wikipedia.org/wiki/Greifswald
- Saarbrücken (49.24°N, 6.99°E): **inside**. Taken over from France before the target date: "Am 30. November 1815 erfolgte [...] die feierliche Besitzergreifung Saarbrückens und der übrigen Saarorte". https://de.wikipedia.org/wiki/Saarbrücken
- Arnsberg (51.4°N, 8.06°E): **inside**. The Duchy of Westphalia, which became Prussian only **after** the target date (see below).
- St. Wendel (49.47°N, 7.17°E): **outside**. The Principality of Lichtenberg (see below).
- Birkenfeld (49.65°N, 7.17°E): **outside**. The Principality of Birkenfeld (see below).
- Meisenheim (49.71°N, 7.67°E): **outside**. The district of Meisenheim (see below).
- Emden (53.37°N, 7.21°E): **outside**. East Frisia, given up before or around the target date: "Preußen musste Ostfriesland an das Königreich Hannover abtreten." https://de.wikipedia.org/wiki/Ostfriesland The day of the hand-over was not found.

## Border changes between 1816 and 1820
**By the source's own dating there is none:** HistoGIS gives this one outline the dates 9 June 1815 to 31 May 1834, and its next outline of Prussia starts on 1 June 1834.

**Reading about the places along the border says otherwise.** The outline shows the settlement of the Congress of Vienna as it stood once the hand-overs listed below were finished (the last one found is dated April 1817). Some of them came after 1 January 1816. **Judgment call: the outline is used for 1 January 1816 anyway**, because the spec asks for this source and the differences found are small pieces of a 275,000 km² kingdom. Their sizes were not measured, except where a page gives one.

Dated after 1 January 1816, and already shown in the outline:
- **The Duchy of Westphalia (around Arnsberg) is inside.** On the target date it still belonged to Hesse-Darmstadt: "Doch dauerte es noch bis zum 15. Juli 1816, bis der Großherzog von Hessen-Darmstadt es abtrat." https://de.wikipedia.org/wiki/Herzogtum_Westfalen This is the largest difference found.
- **The Principality of Lichtenberg (around St. Wendel, 537 km²) is outside.** Saxe-Coburg-Saalfeld took it over later in the year: "Am 11. September 1816 erfolgte die förmliche Besitzergreifung." It was sold to Prussia "mit Staatsvertrag vom 31. Mai 1834", which is the day this outline ends. https://de.wikipedia.org/wiki/Fürstentum_Lichtenberg
- **Meisenheim (176 km²) is outside.** "Der Landgraf von Hessen-Homburg erhielt ebenfalls noch im September 1816 den Kanton Meisenheim". https://de.wikipedia.org/wiki/Département_de_la_Sarre (area: https://de.wikipedia.org/wiki/Oberamt_Meisenheim)
- **Birkenfeld is outside.** "Am 16. April 1817 ging das Gebiet unter dem Namen „Fürstentum Birkenfeld“ in den Besitz der Oldenburger." https://de.wikipedia.org/wiki/Fürstentum_Birkenfeld
- For Lichtenberg, Meisenheim and Birkenfeld, **who held the land on 1 January 1816 was not established**: no page read says so directly. So it is not known whether the outline is right or wrong about them on the target date.

Found in reading, dated 1816 to 1819, and **not tested** against the outline (too small for a hand-typed point, or the place is not named):
- Exchanges with the Schwarzburg principalities, June 1816: "Am 15. Juni 1816 wurde das Amt Ebeleben dem Staatsgebiet von Schwarzburg-Sondershausen angegliedert". https://de.wikipedia.org/wiki/Teilung_des_Königreiches_Sachsen
- The Wittgenstein principalities and Nassau-Siegen: "1817 folgten die Wittgensteiner Fürstentümer [...] sowie das Fürstentum Nassau-Siegen." https://de.wikipedia.org/wiki/Provinz_Westfalen
- The border with the Netherlands, fixed by treaties signed at Aachen (26 June 1816) and Kleve (7 October 1816). https://nl.wikipedia.org/wiki/Traktaat_van_Aken https://nl.wikipedia.org/wiki/Traktaat_van_Kleef
- The border with Saxony, exchanged in places in 1818 and settled on 28 August 1819. https://de.wikipedia.org/wiki/Teilung_des_Königreiches_Sachsen

What was checked: the ten spot checks above, HistoGIS's catalogue of Prussia outlines and their dates, and the pages cited here, read on 2026-11-09. All are encyclopedia pages, not treaties. No treaty text was read.

**Area.** No exact published area for 1816 was found. The German Historical Museum gives a round figure: "Die Fläche der preußischen Herrschaft umfasste nun ungefähr 280.000 km2". https://www.dhm.de/lemo/kapitel/vormaerz-und-revolution/wiener-kongress/neuordnung-europas-181415.html The outline measures 1.6% less than that round figure.

## The foil (`foil.geojson`)
The modern country a model might draw instead of the historical one. It is never scored as truth.
- **Source:** Natural Earth, Admin 0 – Countries, 1:50m, version 5.1.1. Record `Germany` (`ADM0_A3` = `DEU`).
- **File:** `ne_50m_admin_0_countries.zip` from https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip
- **Checksum (SHA-256):** `5fed433373581fa648920435f937d95f2d3c0200e067409c6478dcdf1b853139`
- **Fetched:** 2026-11-09
- **Licence:** public domain. Natural Earth: "All versions of Natural Earth raster + vector map data found on this website are in the public domain." https://www.naturalearthdata.com/about/terms-of-use/
- **Edits:** ring order changed to the GeoJSON convention. No coordinate changed.
