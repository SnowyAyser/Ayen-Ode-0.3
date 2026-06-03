import pytest
from ayen_ode.relinker import relink_text_programmatically, relink_text_with_llm


def test_bidirectional_relinking():
    text = "We arrived at Citadel Vane where Tessaly Vorn was waiting for us."
    
    # We call relink_text_with_llm with empty already_investigated.
    # The bidirectional scanner should dynamically detect Citadel Vane and Tessaly Vorn as new proper nouns,
    # and automatically linkify them as 'object' (item) tags.
    relinked = relink_text_with_llm(None, text, already_investigated={})
    
    assert "<investigate item='citadel vane' cost='1'>Citadel Vane</investigate>" in relinked
    assert "<investigate item='tessaly vorn' cost='1'>Tessaly Vorn</investigate>" in relinked


def test_stem_based_fuzzy_alias_matching():
    already_investigated = {
        "Tessaly Vorn": "character",
        "The Escapement Authority": "faction"
    }
    
    # Test matching stand-alone name stems / aliases
    text = "We spoke with Vorn. Later, Tessaly explained that the Escapement was watching us."
    relinked = relink_text_programmatically(text, already_investigated)
    
    # Stand-alone significant stems should map back to the canonical parent
    assert "<investigate npc='tessaly vorn' cost='1'>Vorn</investigate>" in relinked
    assert "<investigate npc='tessaly vorn' cost='1'>Tessaly</investigate>" in relinked
    assert "<investigate faction='the escapement authority' cost='1'>the Escapement</investigate>" in relinked
    
    # Generic stop words ('the', 'Authority') should NOT be matched standalone
    assert "<investigate faction='the escapement authority' cost='1'>Authority</investigate>" not in relinked
    assert "<investigate faction='the escapement authority' cost='1'>the</investigate>" not in relinked


def test_relinker_double_wrapping_protection():
    already_investigated = {
        "Tessaly Vorn": "character"
    }
    
    # Verify that multi-word match candidates are sorted and matched first,
    # and that subsequent matches (like standalone 'Vorn') do not double-wrap or double-nest inside existing tags.
    text = "Tessaly Vorn is here."
    relinked = relink_text_programmatically(text, already_investigated)
    expected = "<investigate npc='tessaly vorn' cost='1'>Tessaly Vorn</investigate> is here."
    assert relinked == expected


def test_extract_proper_nouns_with_llm():
    from ayen_ode.relinker.parser import extract_proper_nouns_with_llm
    
    class MockContent:
        def __init__(self, text):
            self.text = text
            self.type = "text"
            
    class MockResponse:
        def __init__(self, text):
            self.content = [MockContent(text)]
            
    class MockMessages:
        def __init__(self):
            self.calls = []
        def create(self, **kwargs):
            self.calls.append(kwargs)
            return MockResponse('["Mark of Treachery", "Execution Tower"]')
            
    class MockClient:
        def __init__(self):
            self.messages = MockMessages()
            
    client = MockClient()
    text = "We discovered the Mark of Treachery in the Execution Tower."
    nouns = extract_proper_nouns_with_llm(client, text)
    
    assert nouns == ["Mark of Treachery", "Execution Tower"]
    assert len(client.messages.calls) == 1
    assert "You are a narrative RPG assistant" in client.messages.calls[0]["messages"][0]["content"]


def test_proper_noun_extraction_with_particles():
    from ayen_ode.relinker.parser import extract_heuristic_proper_nouns
    text = "We discovered the Mark of Treachery in the fortress."
    nouns = extract_heuristic_proper_nouns(text)
    assert "Mark of Treachery" in nouns
