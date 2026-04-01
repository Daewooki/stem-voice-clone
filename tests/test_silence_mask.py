import numpy as np
from src.silence_mask import create_mask, apply_mask

def test_create_mask_detects_silence():
    sr = 44100
    silence1 = np.zeros(2 * sr)
    signal = np.random.randn(2 * sr) * 0.1
    silence2 = np.zeros(1 * sr)
    audio = np.concatenate([silence1, signal, silence2])

    mask = create_mask(audio, sr)

    assert len(mask) == len(audio)
    assert np.mean(mask[:sr]) < 0.1
    assert np.mean(mask[2*sr:4*sr]) > 0.8
    assert np.mean(mask[4*sr:]) < 0.1

def test_apply_mask_silences_hallucination():
    sr = 44100
    original = np.concatenate([np.zeros(sr), np.ones(sr) * 0.5])
    converted = np.ones(2 * sr) * 0.3

    mask = create_mask(original, sr, threshold=0.01)
    result = apply_mask(converted, mask)

    assert np.sqrt(np.mean(result[:sr]**2)) < 0.01
    assert np.sqrt(np.mean(result[sr:]**2)) > 0.1
