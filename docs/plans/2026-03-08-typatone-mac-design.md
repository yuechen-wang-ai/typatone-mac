# Typatone-Mac Design

## Overview
System-wide macOS app that plays a unique musical note for every keypress, inspired by Typatone.com. Runs as a lightweight Python background script.

## Architecture
Single Python script with 3 components:
- **Listener** — `pynput` global keyboard hook, filters for relevant keys
- **Sound engine** — `pygame.mixer` with pre-generated synthesized tones
- **Key mapper** — maps each key to a pentatonic note across ~2.5 octaves

## Note Mapping
- Pentatonic scale (C, D, E, G, A) spanning C3 to E5
- 26 letters + 10 digits + punctuation = ~40 keys mapped to ~30 unique pitches
- Keyboard position determines pitch: bottom row = lower, top row = higher

## Special Keys
- Space — soft percussive click
- Enter — deeper thud/chime
- Backspace — short descending tone
- Modifiers (Shift, Cmd, Ctrl, Alt) — silent

## Sound Generation
- On startup, synthesize all tones programmatically using numpy sine waves with ADSR envelope
- Short duration (~150-200ms) so notes don't overlap
- Cached as pygame Sound objects in memory

## Runtime
- `pygame.mixer` initialized with low latency settings
- Multiple channels so rapid typing doesn't cut off previous notes
- Ctrl+C to quit cleanly

## Dependencies
- `pynput` — global keypress listener
- `pygame` — audio playback
- `numpy` — tone synthesis

## Non-goals
- No Docker, no server, no GUI
- No sampled instrument packs in v1 (future enhancement)
