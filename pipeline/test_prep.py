"""The one rule in pipeline/prep.py that is more than cutting a record out of a file: which lakes leave the truth."""

from shapely import MultiPolygon, box

from pipeline.prep import cut_edge_lakes


def test_lakes_that_reach_the_edge_are_cut_out_and_lakes_wholly_inside_stay():
    country = MultiPolygon([box(0, 0, 10, 10)])
    lakes = [
        ("on the border", MultiPolygon([box(9, 4, 11, 6)])),         # the border runs through it
        ("joined to it", MultiPolygon([box(7, 4, 9, 6)])),           # wholly inside, but one water with the first
        ("joined to that", MultiPolygon([box(6, 4, 7, 5)])),         # a chain of lakes is followed to its end
        ("touching the coast", MultiPolygon([box(0, 8, 1, 9)])),     # inside, with one side on the edge
        ("wholly inside", MultiPolygon([box(2, 2, 3, 3)])),          # stays: leaving it out would need a hole
        ("elsewhere", MultiPolygon([box(20, 20, 21, 21)])),
    ]
    land, cut = cut_edge_lakes(country, lakes)
    assert cut == ["joined to it", "joined to that", "on the border", "touching the coast"]
    assert land.area == 100 - 2 - 4 - 1 - 1          # only the half of the border lake that lay inside is lost
    assert land.contains(box(2, 2, 3, 3))            # the interior lake is still counted as land
    assert all(len(piece.interiors) == 0 for piece in land.geoms)

    assert cut_edge_lakes(country, lakes[4:]) == (country, [])
