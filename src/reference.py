"""Extract the best N-second vocal segment from a reference audio file."""
import numpy as np
import librosa
import soundfile as sf


def extract_best_segment(
    input_path: str,
    output_path: str,
    duration: float = 25.0,
    sr: int = 44100,
) -> str:
    """Find the segment with highest RMS energy and save it."""
    y, _ = librosa.load(input_path, sr=sr, mono=True)
    window = int(duration * sr)

    if len(y) <= window:
        sf.write(output_path, y, sr)
        return output_path

    best_start = 0
    best_rms = 0.0
    step = sr

    for start in range(0, len(y) - window, step):
        chunk = y[start : start + window]
        rms = float(np.sqrt(np.mean(chunk**2)))
        if rms > best_rms:
            best_rms = rms
            best_start = start

    segment = y[best_start : best_start + window]
    sf.write(output_path, segment, sr)
    return output_path
