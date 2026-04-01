"""Generate and apply silence masks to prevent SVC hallucination in silent regions."""
import numpy as np
from scipy.ndimage import uniform_filter1d


def create_mask(
    audio: np.ndarray,
    sr: int,
    frame_ms: float = 50.0,
    threshold: float = 0.003,
    fade_ms: float = 10.0,
) -> np.ndarray:
    """Create a binary mask: 1 where vocals exist, 0 where silent."""
    frame_len = int(sr * frame_ms / 1000)
    fade_len = max(int(sr * fade_ms / 1000), 1)
    mask = np.zeros(len(audio))

    for i in range(0, len(audio) - frame_len, frame_len):
        chunk = audio[i : i + frame_len]
        rms = float(np.sqrt(np.mean(chunk**2)))
        if rms > threshold:
            mask[i : i + frame_len] = 1.0

    mask = uniform_filter1d(mask, size=fade_len)
    return mask


def apply_mask(converted: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Apply silence mask to converted audio."""
    min_len = min(len(converted), len(mask))
    result = converted[:min_len].copy()
    result *= mask[:min_len]
    return result
