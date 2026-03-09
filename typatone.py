import numpy as np

SAMPLE_RATE = 44100


def generate_tone(frequency: float, duration: float, volume: float = 0.3) -> np.ndarray:
    """Generate a sine wave tone with ADSR envelope. Returns int16 numpy array."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    wave = np.sin(2 * np.pi * frequency * t)

    envelope = np.ones(n_samples)
    attack = int(n_samples * 0.1)
    decay = int(n_samples * 0.1)
    release = int(n_samples * 0.3)
    sustain_level = 0.7

    if attack > 0:
        envelope[:attack] = np.linspace(0, 1, attack)
    if decay > 0:
        envelope[attack : attack + decay] = np.linspace(1, sustain_level, decay)
    envelope[attack + decay : n_samples - release] = sustain_level
    if release > 0:
        envelope[n_samples - release :] = np.linspace(sustain_level, 0, release)

    wave = wave * envelope * volume
    return (wave * 32767).astype(np.int16)
