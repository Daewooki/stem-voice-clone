# stem-voice-clone

**[한국어](README_ko.md)** | English

**Multi-stem singing voice cloning toolkit.**
Clone any singing voice onto every vocal stem track — preserving all layers.

> Works with any audio file, but **shines with multi-stem tracks** — main vocals, harmonies, ad-libs, all preserved.

---

## The Problem

Existing AI voice cloning tools process a **single vocal track**. But professionally produced songs contain multiple vocal layers:

- **Main vocal** — the lead singing voice
- **Backing vocals (BGV)** — harmonies, chorus, "ooh"s and "aah"s
- **Ad-libs** — vocal flourishes, ad-libbed phrases
- **Vocal effects** — processed or layered vocal textures

When you separate vocals from a mixed song (e.g., with Demucs) and convert that one track, **all these layers collapse into one**. The result sounds thin, flat, and loses the production quality of the original.

## The Solution

**stem-voice-clone** takes a different approach: if you have the original vocal stems, it converts **each stem individually** and reassembles them. Every vocal layer is preserved.

| | Single Track (existing tools) | Multi-Stem (stem-voice-clone) |
|---|---|---|
| Input | 1 audio file | Folder of vocal stems |
| Process | Separate → convert 1 track | Convert each stem separately |
| Vocal layers | Merged into one | Each preserved individually |
| Harmonies/BGV | Lost or degraded | Fully preserved |
| Ad-libs | Mixed in, hard to distinguish | Individually converted |
| Result quality | Thin, flat | **Full, production-quality** |

No stems? No problem — **Single mode** auto-separates vocals with [Demucs](https://github.com/facebookresearch/demucs) and converts them. You still get a result, just without the multi-layer benefit.

---

## Demo

All demo audio is AI-generated with [Suno](https://suno.com/) — fully copyright-free.

**[Listen to the Before/After comparison](https://daewooki.github.io/stem-voice-clone/)**

| Original Song | Target Voice | Converted Result |
|:---:|:---:|:---:|
| [Play](docs/audio/original.mp4) | [Play](docs/audio/target.mp4) | [Play](docs/audio/converted.mp4) |
| Pop ballad, male vocal | Soft ballad, female vocal | Same song, new voice |

> Each vocal stem (main + backing vocals) was converted **individually** — this is what preserves the full layered sound.

---

## Quick Start

### Requirements

- **Python 3.10+**
- **NVIDIA GPU** with 6GB+ VRAM
- **CUDA** (11.8 or newer)

### Installation

```bash
git clone --recursive https://github.com/Daewooki/stem-voice-clone.git
cd stem-voice-clone

# Windows
install.bat

# Linux/Mac
chmod +x install.sh && ./install.sh
```

The install script will:
1. Create a Python virtual environment
2. Install PyTorch with CUDA support
3. Install all dependencies
4. Download the YingMusic-SVC model checkpoint (~700MB, automatic on first run)

### Usage

**Interactive mode** — just run it, it will ask for inputs:
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
# Multi-stem mode (recommended)
python convert.py ./my_stems/ --ref singer.mp3 --output ./result/

# Single file mode (auto-separates vocals with Demucs)
python convert.py song.mp3 --ref singer.mp3

# Output individual tracks only (skip auto-mix)
python convert.py ./stems/ --ref singer.mp3 --no-mix
```

**Try with the included demo:**
```bash
python convert.py ./examples/demo_stems/ --ref ./examples/reference_voice.wav
```

---

## How It Works

### Architecture

```
                         ┌─────────────────────────────────┐
                         │     YingMusic-SVC (Zero-shot)    │
                         │                                   │
                         │  Whisper ──> Content (lyrics)     │
                         │  RMVPE ───> F0 (pitch)           │
                         │  CAMPPlus ─> Style (voice timbre) │
                         │         ↓                         │
                         │  DiT + Flow Matching ──> Output   │
                         └─────────────────────────────────┘
```

### Stem Mode (recommended)

Each vocal stem is converted independently, then reassembled with the original instrumental:

```
Vocal Stem 1  ──> SVC ──> Silence Mask ──> Clean Track 1 ─┐
Vocal Stem 2  ──> SVC ──> Silence Mask ──> Clean Track 2  ├──> Mix
...                                                        │
Vocal Stem N  ──> SVC ──> Silence Mask ──> Clean Track N ──┤
Instrumental  ─────────────────────────────────────────────┘
```

### Single Mode

When you don't have stems, the tool auto-separates vocals first:

```
Audio File ──> Demucs ──> Vocals    ──> SVC ──> Converted Vocal ─┐
                      └── No Vocals ─────────────────────────────┘──> Mix
```

---

## Key Technical Details

### Silence Masking

SVC models tend to "hallucinate" audio in silent regions — generating faint sounds where the original is completely silent. We solve this by creating a mask from the original stem and applying it to the converted output. Silence stays silent.

### Per-Track Volume Matching

Each converted track is gain-matched to its original's RMS level. This ensures the vocal balance of the original mix is preserved after conversion.

### Auto Reference Extraction

You can provide any length of reference audio. The tool automatically finds the most energetic 25-second segment — the optimal length for YingMusic-SVC.

### Single Model Load

The SVC model loads once and processes all stems sequentially. No redundant model loading, even for 15+ stem tracks.

---

## Input

### Folder Structure

The scanner auto-detects your folder structure:

**With subfolders (recommended):**
```
my_stems/
├── Main/
│   ├── vocal_main_1.wav
│   ├── vocal_main_2.wav
│   └── vocal_adlib.wav
├── BGV/
│   ├── vocal_bgv_1.wav
│   └── vocal_bgv_2.wav
└── instrumental.wav
```

**Flat structure (also works):**
```
my_stems/
├── vocal_verse.wav
├── vocal_chorus.wav
├── bgv_harmony.wav
└── instrumental.wav
```

### Auto-Classification Rules

| Classification | Keywords / Rules |
|---|---|
| **Vocal** (converted) | Files in `Main/`, `BGV/`, `Vocal/` folders, or filenames containing: `vocal`, `voice`, `main`, `bgv`, `chorus`, `harmony`, `backing`, `adlib`, `lead` |
| **Instrumental** (kept as-is) | Filenames containing: `instrumental`, `inst`, `karaoke`, `bgm`, `mr` |

### Reference Voice

- Any audio format (WAV, MP3, FLAC, etc.)
- 15–25 seconds of **singing** voice works best
- The tool auto-extracts the best segment if your file is longer
- **Tip:** Use a reference voice with a similar genre/energy to your source for best results

---

## Output

```
output/
├── clean/              # Individual converted tracks
│   ├── vocal_main_1.wav
│   ├── vocal_main_2.wav
│   ├── vocal_bgv_1.wav
│   └── ...
├── mix_final.wav       # Auto-mixed result (all tracks + instrumental)
└── _raw/               # Raw SVC output (before silence masking)
```

**Pro tip:** For the best results, import the `clean/` tracks + your original instrumental into [Audacity](https://www.audacityteam.org/) or your DAW and mix manually. The auto-mix is convenient, but manual mixing gives you full control.

---

## Where to Get Stems

| Source | Description |
|---|---|
| **Your DAW** | Export stems from FL Studio, Logic Pro, Ableton, etc. |
| **AI music generators** | [Suno](https://suno.com/), [Udio](https://udio.com/) can export stems |
| **Remix packs** | Many artists release official stems for remix contests |
| **Creative Commons** | [Cambridge-MT](https://www.cambridge-mt.com/ms/mtk/), [MUSDB18](https://sigsep.github.io/datasets/musdb.html) |
| **No stems at all?** | Use Single mode — it works with any audio file |

---

## Performance

Measured on NVIDIA RTX 3070 (8GB VRAM):

| Step | Time |
|---|---|
| Model loading | ~30s (first run only) |
| Per-track conversion (100 diffusion steps) | ~45s |
| Silence masking + volume matching | ~5s/track |
| 17-track song (e.g., 5 main + 12 BGV) | ~15 min total |

---

## Powered By

- **[YingMusic-SVC](https://github.com/GiantAILab/YingMusic-SVC)** — State-of-the-art zero-shot singing voice conversion ([paper](https://arxiv.org/abs/2512.04793))
- **[Demucs](https://github.com/facebookresearch/demucs)** — Music source separation by Meta
- **[PyTorch](https://pytorch.org/)** — Deep learning framework

---

## Contributing

Contributions are welcome! Feel free to open issues or pull requests.

## License

[MIT](LICENSE)
