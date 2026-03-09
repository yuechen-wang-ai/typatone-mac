import numpy as np
import pytest

from typatone import generate_tone, SAMPLE_RATE


def test_generate_tone_returns_numpy_array():
    tone = generate_tone(440.0, 0.15)
    assert isinstance(tone, np.ndarray)


def test_generate_tone_correct_length():
    duration = 0.15
    tone = generate_tone(440.0, duration)
    expected_samples = int(SAMPLE_RATE * duration)
    assert abs(len(tone) - expected_samples) <= SAMPLE_RATE * 0.01


def test_generate_tone_amplitude_within_range():
    tone = generate_tone(440.0, 0.15)
    assert tone.max() <= 32767
    assert tone.min() >= -32768


def test_generate_tone_different_frequencies_differ():
    tone_a = generate_tone(440.0, 0.15)
    tone_b = generate_tone(880.0, 0.15)
    assert not np.array_equal(tone_a, tone_b)


def test_generate_tone_starts_and_ends_near_zero():
    """ADSR envelope should fade in and out."""
    tone = generate_tone(440.0, 0.2)
    n = len(tone)
    start_max = np.abs(tone[: n // 20]).max()
    end_max = np.abs(tone[-n // 20 :]).max()
    peak = np.abs(tone).max()
    assert start_max < peak * 0.5
    assert end_max < peak * 0.5
