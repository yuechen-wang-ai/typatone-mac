import numpy as np
import pygame
import pygame.sndarray

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


def _build_pentatonic_scale() -> list[float]:
    """Build pentatonic notes from C3 to ~E5."""
    base_notes = [261.63, 293.66, 329.63, 392.00, 440.00]  # C4, D4, E4, G4, A4
    scale = []
    for octave_offset in [-1, 0, 1]:
        for note in base_notes:
            freq = note * (2 ** octave_offset)
            scale.append(round(freq, 2))
    return sorted(scale)


PENTATONIC_SCALE = _build_pentatonic_scale()

_BOTTOM_ROW = list("zxcvbnm,./")
_HOME_ROW = list("asdfghjkl;'")
_TOP_ROW = list("qwertyuiop[]")
_NUMBER_ROW = list("1234567890-=")
_ALL_KEYS = _BOTTOM_ROW + _HOME_ROW + _TOP_ROW + _NUMBER_ROW

KEY_TO_FREQ: dict[str, float] = {}
for i, key in enumerate(_ALL_KEYS):
    KEY_TO_FREQ[key] = PENTATONIC_SCALE[i % len(PENTATONIC_SCALE)]

SPECIAL_KEYS: dict[str, str] = {
    "space": "click",
    "enter": "thud",
    "backspace": "descend",
}

_SPECIAL_FREQS = {
    "space": 800.0,
    "enter": 150.0,
    "backspace": 500.0,
}

SILENT_KEYS = {"shift", "cmd", "ctrl", "alt", "shift_r", "cmd_r", "ctrl_r", "alt_r", "caps_lock", "tab"}


def get_note_frequency(key_name: str) -> float | None:
    """Return frequency for a key, or None if silent."""
    key_name = key_name.lower()
    if key_name in SILENT_KEYS:
        return None
    if key_name in _SPECIAL_FREQS:
        return _SPECIAL_FREQS[key_name]
    return KEY_TO_FREQ.get(key_name)


class SoundEngine:
    def __init__(self):
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self._build_sounds()

    def _build_sounds(self):
        for key, freq in KEY_TO_FREQ.items():
            tone = generate_tone(freq, 0.18)
            self.sounds[key] = pygame.sndarray.make_sound(tone)

        click = generate_tone(800.0, 0.05, volume=0.15)
        self.sounds["space"] = pygame.sndarray.make_sound(click)

        thud = generate_tone(150.0, 0.12, volume=0.25)
        self.sounds["enter"] = pygame.sndarray.make_sound(thud)

        desc = generate_tone(500.0, 0.1, volume=0.2)
        self.sounds["backspace"] = pygame.sndarray.make_sound(desc)

    def play(self, key_name: str):
        key_name = key_name.lower()
        if key_name in SILENT_KEYS:
            return
        sound = self.sounds.get(key_name)
        if sound:
            sound.play()

    def cleanup(self):
        pygame.mixer.quit()
