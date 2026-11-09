from pipeline.verify import missing_tiles


def test_every_library_imports_and_a_missing_tile_is_caught():
    """The pinned Python has a working build of each library in specs/tech-stack.md, and the verify command's
    one piece of logic (a strip that lacks a model's tile) fails loudly."""
    import anthropic, numpy, PIL, pyproj, shapely  # noqa: F401

    full = {"id": "usa", "models": [{"id": "a"}, {"id": "b"}]}
    short = {"id": "chile", "models": [{"id": "a"}]}
    assert missing_tiles({"targets": [full, full]}) == []
    assert missing_tiles({"targets": [full, short]}) == ["chile: no tile for b"]
