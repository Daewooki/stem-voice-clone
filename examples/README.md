# Examples

This folder contains demo audio files generated with [Suno AI](https://suno.com/) — fully copyright-free.

## Quick Demo

```bash
python convert.py ./examples/demo_stems/ --ref ./examples/reference_voice.wav --output ./examples/demo_output/
```

## Files

```
examples/
├── demo_stems/                 # Source song (to be converted)
│   ├── Main/
│   │   └── vocal_main.wav      # Lead vocal stem
│   ├── BGV/
│   │   └── vocal_bgv.wav       # Backing vocal / chorus stem
│   └── instrumental.wav        # Instrumental track (kept as-is)
├── reference_voice.wav         # Target voice (the voice to clone)
└── demo_output/                # Output (generated after running)
    ├── clean/                  # Individual converted tracks
    │   ├── vocal_main.wav
    │   └── vocal_bgv.wav
    └── mix_final.wav           # All tracks mixed together
```

## File Naming Convention

The scanner auto-detects vocals vs instrumental by **folder name** and **filename keywords**.

### Vocal detection (any of these):
- Files inside `Main/`, `BGV/`, `Vocal/`, `Vocals/`, `Chorus/`, `Backing/` folders
- Filenames containing: `vocal`, `voice`, `main`, `bgv`, `chorus`, `harmony`, `backing`, `adlib`, `lead`, `intro`, `outro`

### Instrumental detection:
- Filenames containing: `instrumental`, `inst`, `karaoke`, `bgm`, `mr`, `accompaniment`

### Recommended folder structure:
```
my_stems/
├── Main/           # Main vocals (lead, verse, chorus takes)
│   ├── vocal_main_1.wav
│   ├── vocal_main_2.wav
│   └── vocal_adlib.wav
├── BGV/            # Background vocals (harmonies, chorus)
│   ├── vocal_bgv_1.wav
│   └── vocal_bgv_2.wav
└── instrumental.wav
```

## Where to Find Stems

- **Your own DAW projects** (FL Studio, Logic Pro, Ableton, etc.)
- **AI music generators** — [Suno](https://suno.com/), [Udio](https://udio.com/) export stems
- **Creative Commons stems** — [Cambridge-MT](https://www.cambridge-mt.com/ms/mtk/), [MUSDB18](https://sigsep.github.io/datasets/musdb.html)
- **No stems?** — Use Single mode: `python convert.py song.mp3 --ref voice.wav` (auto-separates with Demucs)
