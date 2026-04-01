"""CLI entry point: argument parsing + interactive mode."""
import argparse
import os
import sys

from src import __version__


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="stem-voice-clone",
        description="Multi-stem singing voice cloning toolkit. "
                    "Clone any voice onto every stem track.",
    )
    parser.add_argument("input", nargs="?", help="Input folder (stems) or audio file")
    parser.add_argument("--ref", "-r", help="Reference voice file (mp3/wav)")
    parser.add_argument("--output", "-o", help="Output folder (default: ./output)")
    parser.add_argument("--steps", type=int, default=100, help="Diffusion steps (default: 100)")
    parser.add_argument("--no-mix", action="store_true", help="Skip auto-mix, output individual tracks only")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args(argv)

    # Interactive mode if missing required args
    if not args.input:
        print(f"\n  stem-voice-clone v{__version__}")
        print(f"  Multi-stem singing voice cloning toolkit\n")
        args.input = input("  [1/3] Input path (stems folder or audio file): ").strip().strip('"')

    if not args.ref:
        args.ref = input("  [2/3] Reference voice file: ").strip().strip('"')

    if not args.output:
        args.output = input("  [3/3] Output folder (Enter for ./output): ").strip().strip('"')
        if not args.output:
            args.output = "./output"

    return args


def main(argv=None):
    args = parse_args(argv)

    # Validate inputs
    if not os.path.exists(args.input):
        print(f"  Error: Input not found: {args.input}")
        sys.exit(1)
    if not os.path.exists(args.ref):
        print(f"  Error: Reference file not found: {args.ref}")
        sys.exit(1)

    # Import heavy modules only after validation
    from src.scanner import scan_input
    from src.reference import extract_best_segment
    from src.converter import load_model, convert_and_clean, convert_track
    from src.separator import separate_vocals
    from src.mixer import mix_stems

    os.makedirs(args.output, exist_ok=True)

    # 1. Scan input
    scan = scan_input(args.input)
    print(f"\n  Mode: {scan['mode'].upper()}")

    # 2. Prepare reference (use abspath to avoid mixed separator issues on Windows)
    ref_path = os.path.abspath(os.path.join(args.output, "_ref_extracted.wav"))
    extract_best_segment(args.ref, ref_path)
    print(f"  Reference: {os.path.basename(args.ref)} (best 25s extracted)")

    # 3. Load model
    models, model_args = load_model()
    model_args.diffusion_steps = args.steps

    if scan["mode"] == "single":
        # Single mode: separate -> convert -> mix
        print(f"\n  Separating vocals...")
        sep = separate_vocals(scan["audio_file"], os.path.join(args.output, "_separated"))

        print(f"  Converting vocal...")
        convert_track(sep["vocals"], ref_path, args.output, models, model_args)
        print(f"\n  Done! Output in: {args.output}")

    else:
        # Stem mode: convert each track
        tracks = scan["vocal_tracks"]
        print(f"  Vocal tracks: {len(tracks)}")
        if scan["instrumental"]:
            print(f"  Instrumental: {os.path.basename(scan['instrumental'])}")

        print(f"\n  Converting {len(tracks)} tracks...\n")

        clean_paths = []
        for i, track in enumerate(tracks):
            name = os.path.basename(track)
            print(f"  [{i+1}/{len(tracks)}] {name}")
            try:
                clean = convert_and_clean(
                    source_path=track,
                    original_path=track,
                    target_path=ref_path,
                    output_dir=args.output,
                    models=models,
                    args=model_args,
                )
                clean_paths.append(clean)
                print(f"           -> done")
            except Exception as e:
                print(f"           -> error: {e}")

        # Auto-mix unless --no-mix
        if not args.no_mix and scan["instrumental"] and clean_paths:
            mix_path = os.path.join(args.output, "mix_final.wav")
            mix_stems(clean_paths, scan["instrumental"], mix_path)
            print(f"\n  Final mix: {mix_path}")

        print(f"\n  Clean tracks: {os.path.join(args.output, 'clean')}")
        print(f"  Done!")
