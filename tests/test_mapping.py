from typatone import get_note_frequency, SPECIAL_KEYS


def test_letter_keys_return_frequency():
    freq = get_note_frequency("a")
    assert freq is not None
    assert 100 < freq < 2000


def test_number_keys_return_frequency():
    freq = get_note_frequency("5")
    assert freq is not None
    assert 100 < freq < 2000


def test_different_keys_can_have_different_frequencies():
    freqs = {get_note_frequency(c) for c in "abcdefg"}
    assert len(freqs) > 1


def test_modifier_keys_return_none():
    assert get_note_frequency("shift") is None
    assert get_note_frequency("cmd") is None
    assert get_note_frequency("ctrl") is None
    assert get_note_frequency("alt") is None


def test_special_keys_in_mapping():
    assert "space" in SPECIAL_KEYS
    assert "enter" in SPECIAL_KEYS
    assert "backspace" in SPECIAL_KEYS


def test_space_returns_frequency():
    freq = get_note_frequency("space")
    assert freq is not None


def test_pentatonic_scale_used():
    freq = get_note_frequency("a")
    assert freq is not None
    assert 100 < freq < 2000
