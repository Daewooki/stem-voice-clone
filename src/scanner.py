"""Auto-detect input structure: stem folder vs single audio file.

Classification rules (in order):
1. Files in Main/ or BGV/ subfolders → vocal
2. Filename contains a vocal keyword (vocal, voice, bgv, chorus, etc.) → vocal
3. Filename contains an instrumental keyword (inst, instrumental, karaoke, etc.) → instrumental
4. Remaining audio files → vocal (safer default for SVC)
"""
import os

AUDIO_EXTS = {".wav", ".flac", ".mp3", ".ogg", ".m4a"}

INST_KEYWORDS = {"instrumental", "inst", "karaoke", "bgm", "mr", "accompaniment"}
VOCAL_KEYWORDS = {
    "vocal", "voice", "main", "bgv", "chorus", "harmony",
    "adl", "adlib", "ad-lib", "intro", "outro", "backing",
    "lead", "singer", "sing",
}
VOCAL_FOLDERS = {"main", "bgv", "vocal", "vocals", "chorus", "backing"}


def _is_audio(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in AUDIO_EXTS


def _classify(filepath: str) -> str:
    """Classify a file as 'vocal' or 'instrumental'.

    Priority: folder name > vocal keywords > instrumental keywords > default vocal.
    """
    filename = os.path.splitext(os.path.basename(filepath))[0].lower()
    parent = os.path.basename(os.path.dirname(filepath)).lower()

    # Rule 1: Parent folder is a known vocal folder
    if parent in VOCAL_FOLDERS:
        return "vocal"

    # Rule 2: Filename contains vocal keyword
    if any(kw in filename for kw in VOCAL_KEYWORDS):
        return "vocal"

    # Rule 3: Filename contains instrumental keyword
    if any(kw in filename for kw in INST_KEYWORDS):
        return "instrumental"

    # Rule 4: Default — treat as vocal (safer for SVC)
    return "vocal"


def scan_input(input_path: str) -> dict:
    """Scan input path and determine mode + file list.

    Returns dict with:
        mode: "stem" | "single"
        vocal_tracks: list of absolute paths (stem mode)
        instrumental: absolute path or None (stem mode)
        audio_file: absolute path (single mode)
    """
    input_path = os.path.abspath(input_path)

    # Single file → single mode
    if os.path.isfile(input_path):
        return {"mode": "single", "audio_file": input_path}

    # Collect all audio files
    audio_files = []
    for root, dirs, files in os.walk(input_path):
        for f in files:
            if _is_audio(f):
                audio_files.append(os.path.join(root, f))

    if not audio_files:
        raise FileNotFoundError(f"No audio files found in {input_path}")

    # One file → single mode
    if len(audio_files) == 1:
        return {"mode": "single", "audio_file": audio_files[0]}

    # Multiple files → stem mode, classify each
    vocal_tracks = []
    instrumental = None

    for fp in sorted(audio_files):
        role = _classify(fp)
        if role == "instrumental":
            instrumental = fp
        else:
            vocal_tracks.append(fp)

    return {
        "mode": "stem",
        "vocal_tracks": vocal_tracks,
        "instrumental": instrumental,
    }
