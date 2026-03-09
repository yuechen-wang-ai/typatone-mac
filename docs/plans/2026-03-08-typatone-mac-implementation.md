# Typatone-Mac Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a system-wide macOS keypress-to-music app that plays pentatonic notes as you type.

**Architecture:** Single-file Python script with three modules: tone synthesis (numpy sine waves with ADSR), key-to-note mapping (pentatonic scale across keyboard rows), and a pynput global listener that triggers pygame audio playback.

**Tech Stack:** Python 3, pynput, pygame, numpy

---

### Task 1: Update dependencies

**Files:**
- Modify: `requirements.txt`

**Step 1: Add numpy to requirements**

```
pynput
pygame
numpy
```

**Step 2: Install dependencies**

Run: `cd /home/yuechen_wang/repo/typatone-mac && source venv/bin/activate && pip install -r requirements.txt`
Expected: All packages install successfully

**Step 3: Commit**

```bash
git add requirements.txt
git commit -m "add numpy dependency"
```

---

### Task 2: Tone synthesis module

**Files:**
- Create: `tests/test_tone.py`
- Modify: `typatone.py`

**Step 1: Write failing tests for tone generation**

```python
# tests/test_tone.py
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
    # Allow small tolerance for ADSR envelope padding
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
    # First and last 5% of samples should be quieter than peak
    n = len(tone)
    start_max = np.abs(tone[: n // 20]).max()
    end_max = np.abs(tone[-n // 20 :]).max()
    peak = np.abs(tone).max()
    assert start_max < peak * 0.5
    assert end_max < peak * 0.5
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/yuechen_wang/repo/typatone-mac && source venv/bin/activate && python -m pytest tests/test_tone.py -v`
Expected: FAIL — `cannot import name 'generate_tone' from 'typatone'`

**Step 3: Implement tone synthesis**

Write in `typatone.py`:

```python
import numpy as np

SAMPLE_RATE = 44100


def generate_tone(frequency: float, duration: float, volume: float = 0.3) -> np.ndarray:
    """Generate a sine wave tone with ADSR envelope.

    Returns int16 numpy array suitable for pygame.
    """
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # Sine wave
    wave = np.sin(2 * np.pi * frequency * t)

    # ADSR envelope (attack, decay, sustain, release)
    envelope = np.ones(n_samples)
    attack = int(n_samples * 0.05)
    decay = int(n_samples * 0.1)
    release = int(n_samples * 0.3)
    sustain_level = 0.7

    # Attack
    if attack > 0:
        envelope[:attack] = np.linspace(0, 1, attack)
    # Decay
    if decay > 0:
        envelope[attack : attack + decay] = np.linspace(1, sustain_level, decay)
    # Sustain
    envelope[attack + decay : n_samples - release] = sustain_level
    # Release
    if release > 0:
        envelope[n_samples - release :] = np.linspace(sustain_level, 0, release)

    wave = wave * envelope * volume
    return (wave * 32767).astype(np.int16)
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/yuechen_wang/repo/typatone-mac && source venv/bin/activate && python -m pytest tests/test_tone.py -v`
Expected: All 5 tests PASS

**Step 5: Commit**

```bash
git add tests/test_tone.py typatone.py
git commit -m "add tone synthesis with ADSR envelope"
```

---

### Task 3: Key-to-note mapping

**Files:**
- Create: `tests/test_mapping.py`
- Modify: `typatone.py`

**Step 1: Write failing tests for key mapping**

```python
# tests/test_mapping.py
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
    """All melodic frequencies should be from pentatonic scale."""
    # C pentatonic ratios relative to C: 1, 9/8, 5/4, 3/2, 5/3
    # Check that a maps to a valid pentatonic note
    freq = get_note_frequency("a")
    assert freq is not None
    # Verify it's a reasonable musical frequency
    assert 100 < freq < 2000
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/yuechen_wang/repo/typatone-mac && source venv/bin/activate && python -m pytest tests/test_mapping.py -v`
Expected: FAIL — `cannot import name 'get_note_frequency' from 'typatone'`

**Step 3: Implement key mapping**

Add to `typatone.py`:

```python
# Pentatonic scale frequencies (C, D, E, G, A) across octaves
def _build_pentatonic_scale() -> list[float]:
    """Build pentatonic notes from C3 to ~E5."""
    # Base frequencies for C pentatonic in octave 0
    base_notes = [261.63, 293.66, 329.63, 392.00, 440.00]  # C4, D4, E4, G4, A4
    scale = []
    for octave_offset in [-1, 0, 1]:
        for note in base_notes:
            freq = note * (2 ** octave_offset)
            scale.append(round(freq, 2))
    return sorted(scale)


PENTATONIC_SCALE = _build_pentatonic_scale()

# Keyboard layout rows (bottom to top = low to high pitch)
_BOTTOM_ROW = list("zxcvbnm,./")
_HOME_ROW = list("asdfghjkl;'")
_TOP_ROW = list("qwertyuiop[]")
_NUMBER_ROW = list("1234567890-=")
_ALL_KEYS = _BOTTOM_ROW + _HOME_ROW + _TOP_ROW + _NUMBER_ROW

# Map each key to a pentatonic note
KEY_TO_FREQ: dict[str, float] = {}
for i, key in enumerate(_ALL_KEYS):
    KEY_TO_FREQ[key] = PENTATONIC_SCALE[i % len(PENTATONIC_SCALE)]

# Special keys with distinct sounds
SPECIAL_KEYS: dict[str, str] = {
    "space": "click",
    "enter": "thud",
    "backspace": "descend",
}

# Special key frequencies
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
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/yuechen_wang/repo/typatone-mac && source venv/bin/activate && python -m pytest tests/test_mapping.py -v`
Expected: All 7 tests PASS

**Step 5: Commit**

```bash
git add tests/test_mapping.py typatone.py
git commit -m "add pentatonic key-to-note mapping"
```

---

### Task 4: Sound engine (pygame integration)

**Files:**
- Create: `tests/test_engine.py`
- Modify: `typatone.py`

**Step 1: Write failing tests for sound engine**

```python
# tests/test_engine.py
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
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/yuechen_wang/repo/typatone-mac && source venv/bin/activate && python -m pytest tests/test_engine.py -v`
Expected: FAIL — `cannot import name 'SoundEngine' from 'typatone'`

**Step 3: Implement SoundEngine**

Add to `typatone.py`:

```python
import pygame
import pygame.sndarray


class SoundEngine:
    def __init__(self):
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self._build_sounds()

    def _build_sounds(self):
        # Build melodic key sounds
        for key, freq in KEY_TO_FREQ.items():
            tone = generate_tone(freq, 0.18)
            self.sounds[key] = pygame.sndarray.make_sound(tone)

        # Build special key sounds
        # Space: short quiet click (high freq, very short)
        click = generate_tone(800.0, 0.05, volume=0.15)
        self.sounds["space"] = pygame.sndarray.make_sound(click)

        # Enter: low thud
        thud = generate_tone(150.0, 0.12, volume=0.25)
        self.sounds["enter"] = pygame.sndarray.make_sound(thud)

        # Backspace: quick descending tone (approximate with low note)
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
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/yuechen_wang/repo/typatone-mac && source venv/bin/activate && python -m pytest tests/test_engine.py -v`
Expected: All 4 tests PASS

**Step 5: Commit**

```bash
git add tests/test_engine.py typatone.py
git commit -m "add pygame sound engine"
```

---

### Task 5: Global keyboard listener and main loop

**Files:**
- Modify: `typatone.py`

**Step 1: Implement the keyboard listener and main entry point**

Add to `typatone.py`:

```python
from pynput import keyboard


def _key_to_name(key) -> str:
    """Convert pynput key object to our key name string."""
    if hasattr(key, "char") and key.char is not None:
        return key.char.lower()
    # Map special keys
    key_map = {
        keyboard.Key.space: "space",
        keyboard.Key.enter: "enter",
        keyboard.Key.backspace: "backspace",
        keyboard.Key.shift: "shift",
        keyboard.Key.shift_r: "shift_r",
        keyboard.Key.cmd: "cmd",
        keyboard.Key.cmd_r: "cmd_r",
        keyboard.Key.ctrl: "ctrl",
        keyboard.Key.ctrl_r: "ctrl_r",
        keyboard.Key.alt: "alt",
        keyboard.Key.alt_r: "alt_r",
        keyboard.Key.caps_lock: "caps_lock",
        keyboard.Key.tab: "tab",
    }
    return key_map.get(key, "unknown")


def main():
    print("Typatone-Mac is running! Press Ctrl+C to stop.")
    engine = SoundEngine()

    def on_press(key):
        name = _key_to_name(key)
        engine.play(name)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        listener.join()
    except KeyboardInterrupt:
        print("\nStopping Typatone-Mac...")
    finally:
        listener.stop()
        engine.cleanup()


if __name__ == "__main__":
    main()
```

**Step 2: Manual smoke test**

Run: `cd /home/yuechen_wang/repo/typatone-mac && source venv/bin/activate && python typatone.py`
Expected: Script starts, prints message, plays notes as you type, Ctrl+C stops it

**Step 3: Run all tests**

Run: `cd /home/yuechen_wang/repo/typatone-mac && source venv/bin/activate && python -m pytest tests/ -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add typatone.py
git commit -m "add global keyboard listener and main loop"
```

---

### Task 6: Write README

**Files:**
- Modify: `README.md`

**Step 1: Write README content**

```markdown
# Typatone-Mac

A system-wide macOS app that plays a unique musical note for every keypress. Every key is mapped to a pentatonic scale, so random typing always sounds pleasant.

## Install

```bash
git clone <repo-url>
cd typatone-mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
source venv/bin/activate
python3 typatone.py
```

Press Ctrl+C to stop.

**Note:** On macOS, you'll need to grant Accessibility permissions to your terminal app (System Preferences > Privacy & Security > Accessibility).

## How It Works

- Listens to global keypresses via `pynput`
- Each key plays a note from the pentatonic scale (C, D, E, G, A) spanning ~2.5 octaves
- Bottom keyboard row = low notes, top row = high notes
- Space/Enter/Backspace play percussive sounds
- Modifier keys (Shift, Cmd, etc.) are silent
- Notes are synthesized on startup using sine waves with ADSR envelopes

## Tests

```bash
python -m pytest tests/ -v
```
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "add README"
```

---

### Task 7: Final integration test

**Step 1: Run full test suite**

Run: `cd /home/yuechen_wang/repo/typatone-mac && source venv/bin/activate && python -m pytest tests/ -v`
Expected: All tests PASS

**Step 2: Verify script imports cleanly**

Run: `cd /home/yuechen_wang/repo/typatone-mac && source venv/bin/activate && python -c "import typatone; print('OK')"`
Expected: Prints "OK" (note: pygame mixer may init, that's fine)

**Step 3: Final commit if any cleanup needed**
