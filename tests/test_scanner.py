import os, tempfile, struct, pytest
from src.scanner import scan_input

def _make_wav(path):
    """Create a minimal valid WAV file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sr, bits, channels, duration = 44100, 16, 1, 0.1
    n_samples = int(sr * duration)
    data_size = n_samples * channels * (bits // 8)
    with open(path, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, channels, sr, sr * channels * bits // 8, channels * bits // 8, bits))
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(b"\x00" * data_size)

def test_stem_mode_with_subfolders():
    with tempfile.TemporaryDirectory() as tmp:
        for p in ["Main/vocal_main_1.wav", "Main/vocal_main_2.wav", "BGV/vocal_bgv_1.wav", "instrumental.wav"]:
            _make_wav(os.path.join(tmp, p))
        result = scan_input(tmp)
        assert result["mode"] == "stem"
        assert len(result["vocal_tracks"]) == 3
        assert result["instrumental"] is not None

def test_stem_mode_flat():
    with tempfile.TemporaryDirectory() as tmp:
        for p in ["vocal_main.wav", "vocal_bgv.wav", "instrumental.wav"]:
            _make_wav(os.path.join(tmp, p))
        result = scan_input(tmp)
        assert result["mode"] == "stem"
        assert len(result["vocal_tracks"]) == 2
        assert result["instrumental"] is not None

def test_single_mode_one_file():
    with tempfile.TemporaryDirectory() as tmp:
        _make_wav(os.path.join(tmp, "song.wav"))
        result = scan_input(tmp)
        assert result["mode"] == "single"
        assert result["audio_file"] is not None

def test_backing_vocals_classified_as_vocal():
    with tempfile.TemporaryDirectory() as tmp:
        for p in ["Main/vocal_main.wav", "BGV/backing_vocals.wav", "instrumental.wav"]:
            _make_wav(os.path.join(tmp, p))
        result = scan_input(tmp)
        assert len(result["vocal_tracks"]) == 2

def test_folder_name_takes_priority():
    """Files in Main/ or BGV/ are always vocal regardless of filename."""
    with tempfile.TemporaryDirectory() as tmp:
        for p in ["Main/track_01.wav", "BGV/track_02.wav", "inst.wav"]:
            _make_wav(os.path.join(tmp, p))
        result = scan_input(tmp)
        assert len(result["vocal_tracks"]) == 2
        assert result["instrumental"] is not None
