import pytest
from typatone import SoundEngine


def test_sound_engine_initializes():
    engine = SoundEngine()
    assert engine is not None
    engine.cleanup()


def test_sound_engine_has_sounds_for_keys():
    engine = SoundEngine()
    assert len(engine.sounds) > 0
    engine.cleanup()


def test_sound_engine_play_does_not_crash():
    engine = SoundEngine()
    engine.play("a")
    engine.play("space")
    engine.play("shift")  # silent key, should not crash
    engine.cleanup()


def test_sound_engine_special_keys_have_sounds():
    engine = SoundEngine()
    engine.play("space")
    engine.play("enter")
    engine.play("backspace")
    engine.cleanup()
