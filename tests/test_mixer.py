import numpy as np, soundfile as sf, tempfile, os
from src.mixer import mix_stems

def test_mix_stems_basic():
    sr = 44100
    with tempfile.TemporaryDirectory() as tmp:
        for name in ["vocal1.wav", "vocal2.wav"]:
            audio = np.random.randn(sr * 2) * 0.1
            sf.write(os.path.join(tmp, name), audio, sr)

        inst = np.random.randn(sr * 2) * 0.2
        inst_path = os.path.join(tmp, "inst.wav")
        sf.write(inst_path, inst, sr)

        out_path = os.path.join(tmp, "mix.wav")
        vocals = [os.path.join(tmp, "vocal1.wav"), os.path.join(tmp, "vocal2.wav")]

        mix_stems(vocals, inst_path, out_path)

        assert os.path.exists(out_path)
        result, sr2 = sf.read(out_path)
        assert sr2 == sr
        assert len(result) == sr * 2

def test_mix_stems_different_sample_rates():
    with tempfile.TemporaryDirectory() as tmp:
        vocal = np.random.randn(44100 * 2) * 0.1
        sf.write(os.path.join(tmp, "vocal.wav"), vocal, 44100)

        inst = np.random.randn(48000 * 2) * 0.2
        sf.write(os.path.join(tmp, "inst.wav"), inst, 48000)

        out_path = os.path.join(tmp, "mix.wav")
        mix_stems([os.path.join(tmp, "vocal.wav")], os.path.join(tmp, "inst.wav"), out_path)

        result, sr = sf.read(out_path)
        assert sr == 44100
        assert abs(len(result) / sr - 2.0) < 0.1
