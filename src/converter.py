"""Batch singing voice conversion: load model once, convert all tracks."""
import os
import sys
import argparse
import glob

import torch
import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr

from src.model_manager import get_vendor_path, get_checkpoint_path, get_config_path
from src.silence_mask import create_mask, apply_mask


def _setup_vendor():
    """Add YingMusic-SVC to sys.path and chdir to it."""
    vendor = get_vendor_path()
    if vendor not in sys.path:
        sys.path.insert(0, vendor)
    os.environ["HF_HUB_CACHE"] = os.path.join(vendor, "checkpoints", "hf_cache")
    original_cwd = os.getcwd()
    os.chdir(vendor)
    return original_cwd


def load_model(device: torch.device = torch.device("cuda:0"), fp16: bool = True):
    """Load YingMusic-SVC model once.

    Returns:
        (model_bundle, args_template)
    """
    original_cwd = _setup_vendor()

    from my_inference import load_models_api

    ckpt = get_checkpoint_path()
    config = get_config_path()

    args = argparse.Namespace(
        checkpoint=ckpt,
        config=config,
        cuda=device,
        fp16=fp16,
        diffusion_steps=100,
        length_adjust=1.0,
        inference_cfg_rate=0.7,
        f0_condition=True,
        semi_tone_shift=None,
        output="./outputs",
    )

    print("  Loading YingMusic-SVC model...")
    models = load_models_api(args, device=device)
    print("  Model loaded.")

    return models, args


def convert_track(
    source_path: str,
    target_path: str,
    output_dir: str,
    models,
    args,
    device: torch.device = torch.device("cuda:0"),
) -> str:
    """Convert a single vocal track.

    Returns:
        Path to converted wav file.
    """
    from my_inference import run_inference

    track_name = os.path.splitext(os.path.basename(source_path))[0]
    args.source = source_path
    args.target = target_path
    args.expname = track_name
    args.output = output_dir

    output_path = run_inference(args, models, device=device)
    return output_path


def convert_and_clean(
    source_path: str,
    original_path: str,
    target_path: str,
    output_dir: str,
    models,
    args,
    device: torch.device = torch.device("cuda:0"),
    sr: int = 44100,
) -> str:
    """Convert a track, apply silence mask and volume matching.

    Args:
        source_path: Vocal track to convert.
        original_path: Original track (for silence mask + volume reference).
        target_path: Reference voice file.
        output_dir: Where to save output.
        models: Loaded model bundle.
        args: Args namespace.
        device: CUDA device.
        sr: Target sample rate.

    Returns:
        Path to clean output wav.
    """
    # Normalize all paths to absolute (avoid mixed separator issues on Windows)
    source_path = os.path.abspath(source_path)
    original_path = os.path.abspath(original_path)
    target_path = os.path.abspath(target_path)
    output_dir = os.path.abspath(output_dir)

    # 1. Convert
    raw_dir = os.path.join(output_dir, "_raw")
    os.makedirs(raw_dir, exist_ok=True)
    convert_track(source_path, target_path, raw_dir, models, args, device)

    # Find the output file
    track_name = os.path.splitext(os.path.basename(source_path))[0]
    raw_files = glob.glob(os.path.join(raw_dir, track_name, "*.wav"))
    if not raw_files:
        raise FileNotFoundError(f"No output found for {track_name}")
    raw_path = raw_files[0]

    # 2. Load original and converted
    orig_y, _ = librosa.load(original_path, sr=sr, mono=True)
    conv_y, _ = sf.read(raw_path)
    if conv_y.ndim > 1:
        conv_y = conv_y.mean(axis=-1)

    # 3. Noise reduction
    conv_y = nr.reduce_noise(y=conv_y, sr=sr, prop_decrease=0.3, stationary=True)

    # 4. Volume matching to original
    orig_rms = float(np.sqrt(np.mean(orig_y**2)))
    conv_rms = float(np.sqrt(np.mean(conv_y**2)))
    if conv_rms > 1e-6:
        conv_y = conv_y * (orig_rms / conv_rms)

    # 5. Silence mask
    mask = create_mask(orig_y, sr)
    min_len = min(len(conv_y), len(mask))
    conv_y = apply_mask(conv_y[:min_len], mask[:min_len])

    # 6. Save clean output
    clean_dir = os.path.join(output_dir, "clean")
    os.makedirs(clean_dir, exist_ok=True)
    clean_path = os.path.join(clean_dir, os.path.basename(source_path))
    sf.write(clean_path, conv_y, sr)

    return clean_path
