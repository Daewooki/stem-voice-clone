# stem-voice-clone

**Multi-stem singing voice cloning toolkit.**
Clone any singing voice onto every vocal stem track — preserving all layers.

> Works with any audio file, but **shines with multi-stem tracks** — main vocals, harmonies, ad-libs, all preserved.

---

## Why Multi-Stem?

Existing voice cloning tools convert a single vocal track. When applied to a mixed song, you lose the richness of layered vocal production.

| | Single Track (existing tools) | Multi-Stem (this tool) |
|---|---|---|
| Input | 1 audio file | Folder of vocal stems |
| Vocal layers | Merged into one | Each converted separately |
| Harmonies/BGV | Lost or degraded | Fully preserved |
| Ad-libs | Mixed in | Individually converted |
| Result | Thin, flat | Full, production-quality |

### Demo: Voice Conversion Result

All demo audio is AI-generated with [Suno](https://suno.com/) — fully copyright-free.

**[Listen to the Before/After comparison on the demo page](https://daewook.github.io/stem-voice-clone/)**

| | Original Song | Target Voice | Converted Result |
|---|---|---|---|
| **Description** | Pop ballad (male vocal) | Funk pop (female vocal) | Same song, new voice |
| **Audio** | [Play original](docs/audio/original.mp4) | [Play target](docs/audio/target.mp4) | [Play converted](docs/audio/converted.mp4) |

---

## Quick Start

### Installation

```bash
git clone --recursive https://github.com/Daewooki/stem-voice-clone.git
cd stem-voice-clone

# Windows
install.bat

# Linux/Mac
chmod +x install.sh && ./install.sh
```

**Requirements:** Python 3.10+, NVIDIA GPU (6GB+ VRAM), CUDA

### Usage

**Interactive mode** (just run it):
```bash
python convert.py
```
```
  stem-voice-clone v0.1.0
  Multi-stem singing voice cloning toolkit

  [1/3] Input path (stems folder or audio file): ./my_stems/
  [2/3] Reference voice file: ./singer.mp3
  [3/3] Output folder (Enter for ./output):

  Mode: STEM
  Reference: singer.mp3 (best 25s extracted)
  Vocal tracks: 13
  Instrumental: inst.wav

  Loading YingMusic-SVC model...
  Model loaded.

  Converting 13 tracks...

  [1/13] Vocal Main 1.wav -> done
  [2/13] Vocal Main 2.wav -> done
  ...

  Clean tracks: output/clean/
  Done!
```

**Command-line mode:**
```bash
# Multi-stem mode
python convert.py ./my_stems/ --ref singer.mp3 --output ./result/

# Single file mode (auto-separates vocals with Demucs)
python convert.py song.mp3 --ref singer.mp3

# Individual tracks only (no auto-mix)
python convert.py ./stems/ --ref singer.mp3 --no-mix
```

---

## How It Works

### Stem Mode (recommended)
```
Vocal Stem 1  ──> SVC ──> Silence Mask ──> Clean Track 1 ─┐
Vocal Stem 2  ──> SVC ──> Silence Mask ──> Clean Track 2  ├──> Mix
...                                                        │
Vocal Stem N  ──> SVC ──> Silence Mask ──> Clean Track N ──┤
Instrumental  ─────────────────────────────────────────────┘
```

### Single Mode
```
Audio File ──> Demucs ──> Vocals    ──> SVC ──> Converted Vocal ─┐
                      └── No Vocals ─────────────────────────────┘──> Mix
```

### Key Technical Details

- **Silence Masking**: SVC models hallucinate audio in silent regions. We apply a mask from the original stems to ensure silence stays silent.
- **Per-track Volume Matching**: Each converted track is matched to its original's RMS level.
- **Auto Reference Extraction**: Automatically finds the most energetic 25-second segment from your reference audio.
- **Single Model Load**: The model loads once and converts all tracks sequentially — no redundant loading.

---

## Input Folder Structure

The scanner auto-detects your folder structure:

**With subfolders (recommended):**
```
my_stems/
├── Main/
│   ├── Vocal Main 1.wav
│   ├── Vocal Main 2.wav
│   └── Vocal ADL.wav
├── BGV/
│   ├── BGV 1.wav
│   └── BGV 2.wav
└── inst.wav
```

**Flat structure (also works):**
```
my_stems/
├── vocal_verse.wav
├── vocal_chorus.wav
├── bgv_harmony.wav
└── instrumental.wav
```

Files with keywords like `inst`, `instrumental`, `karaoke`, `bgm` are auto-detected as instrumentals.

---

## Output

```
output/
├── clean/              # Individual converted tracks (load these in your DAW)
│   ├── Vocal Main 1.wav
│   ├── Vocal Main 2.wav
│   ├── BGV 1.wav
│   └── ...
└── mix_final.wav       # Auto-mixed result (all tracks + instrumental)
```

**Pro tip:** For best results, import the `clean/` tracks + your instrumental into [Audacity](https://www.audacityteam.org/) or your DAW and mix manually.

---

## Powered By

- [YingMusic-SVC](https://github.com/GiantAILab/YingMusic-SVC) — State-of-the-art zero-shot singing voice conversion
- [Demucs](https://github.com/facebookresearch/demucs) — Music source separation by Meta

---

## License

MIT
