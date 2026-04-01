#!/bin/bash
set -e
echo "=== stem-voice-clone installer ==="
echo

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found."
    exit 1
fi

echo "[1/4] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Defaults to CUDA 11.8 — change cu118 to cu121 or cu124 for newer CUDA
# See https://pytorch.org/get-started/locally/ for your CUDA version
echo "[2/4] Installing PyTorch with CUDA..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

echo "[3/4] Installing dependencies..."
pip install -r requirements.txt

echo "[4/4] Setting up YingMusic-SVC..."
git submodule update --init --recursive

echo
echo "=== Installation complete! ==="
echo
echo "Usage:"
echo "  source venv/bin/activate"
echo "  python convert.py"
