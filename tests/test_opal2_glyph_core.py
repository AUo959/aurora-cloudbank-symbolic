from modules.opal2.glyph_core import GlyphGenerator

def test_generate_glyph():
    gen = GlyphGenerator(dim=8)
    result = gen.generate("alpha")
    assert result["symbol"] == "alpha"
    assert len(result["vector"]) == 8
    assert isinstance(result["multivector"], str)
    assert result["multivector"] != ""
