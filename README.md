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

**Note:** On macOS, grant Accessibility permissions to your terminal app (System Preferences > Privacy & Security > Accessibility).

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
