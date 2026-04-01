"""Simple additive mixer with automatic resampling."""
import numpy as np
import librosa
import soundfile as sf


def mix_stems(
    vocal_paths: list[str],
    instrumental_path: str | None,
    output_path: str,
    sr: int = 44100,
) -> str:
    """Mix vocal tracks + instrumental by simple addition.

    All files are resampled to the target sr before mixing.
    No compression, no normalization - just addition + peak limiting if needed.
    """
    if instrumental_path:
        inst, _ = librosa.load(instrumental_path, sr=sr, mono=False)
        if inst.ndim == 1:
            inst = np.stack([inst, inst], axis=0)
        mix = inst.T.copy()
    else:
        mix = None

    for vp in vocal_paths:
        y, _ = librosa.load(vp, sr=sr, mono=True)
        y_stereo = np.stack([y, y], axis=-1)

        if mix is None:
            mix = y_stereo
        else:
            min_len = min(len(y_stereo), len(mix))
            mix[:min_len] += y_stereo[:min_len]

    peak = np.max(np.abs(mix))
    if peak > 1.0:
        mix = mix / peak * 0.99

    sf.write(output_path, mix, sr)
    return output_path
