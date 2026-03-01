from modules.opal2.glyph_cache import GlyphCache


def test_cache_store_and_load(tmp_path):
    cache_file = tmp_path / "cache.json"
    cache = GlyphCache(file=str(cache_file))
    assert cache.get("alpha") is None
    data = {"symbol": "alpha", "vector": [1, -1]}
    cache.store("alpha", data)
    cache.save()

    cache2 = GlyphCache(file=str(cache_file))
    assert cache2.get("alpha") == data
