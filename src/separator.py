"""Vocal/instrumental separation using Demucs (for Single mode)."""
import os
import subprocess
import sys


def separate_vocals(
    audio_path: str,
    output_dir: str,
    model: str = "htdemucs",
) -> dict:
    """Separate audio into vocals and instrumental using Demucs.

    Args:
        audio_path: Path to input audio file.
        output_dir: Directory for separated files.
        model: Demucs model name.

    Returns:
        Dict with "vocals" and "no_vocals" paths.
    """
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        sys.executable, "-m", "demucs",
        audio_path,
        "-o", output_dir,
        "--two-stems", "vocals",
        "-n", model,
    ]

    print(f"  Separating vocals from {os.path.basename(audio_path)}...")
    subprocess.run(cmd, check=True)

    track_name = os.path.splitext(os.path.basename(audio_path))[0]
    stem_dir = os.path.join(output_dir, model, track_name)

    return {
        "vocals": os.path.join(stem_dir, "vocals.wav"),
        "no_vocals": os.path.join(stem_dir, "no_vocals.wav"),
    }
