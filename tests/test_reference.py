import numpy as np, soundfile as sf, tempfile, os
from src.reference import extract_best_segment

def test_extract_best_segment():
    sr = 44100
    with tempfile.TemporaryDirectory() as tmp:
        silence = np.zeros(5 * sr)
        loud = np.random.randn(30 * sr) * 0.3
        audio = np.concatenate([silence, loud, silence])
        path = os.path.join(tmp, "ref.wav")
        sf.write(path, audio, sr)

        out_path = os.path.join(tmp, "ref_extracted.wav")
        result = extract_best_segment(path, out_path, duration=25)

        assert os.path.exists(result)
        extracted, sr2 = sf.read(result)
        assert abs(len(extracted) / sr2 - 25.0) < 0.1
        assert np.sqrt(np.mean(extracted**2)) > 0.1

def test_short_audio_returns_full():
    sr = 44100
    with tempfile.TemporaryDirectory() as tmp:
        audio = np.random.randn(10 * sr) * 0.3
        path = os.path.join(tmp, "short.wav")
        sf.write(path, audio, sr)

        out_path = os.path.join(tmp, "short_extracted.wav")
        result = extract_best_segment(path, out_path, duration=25)

        extracted, _ = sf.read(result)
        assert abs(len(extracted) / sr - 10.0) < 0.1
