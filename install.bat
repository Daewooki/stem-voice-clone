@echo off
echo === stem-voice-clone installer ===
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM Create venv
echo [1/4] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install PyTorch (defaults to CUDA 11.8 — change cu118 to cu121 or cu124 for newer CUDA)
REM See https://pytorch.org/get-started/locally/ for your CUDA version
echo [2/4] Installing PyTorch with CUDA...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

REM Install dependencies
echo [3/4] Installing dependencies...
pip install -r requirements.txt

REM Init submodule
echo [4/4] Setting up YingMusic-SVC...
git submodule update --init --recursive

echo.
echo === Installation complete! ===
echo.
echo Usage:
echo   venv\Scripts\activate.bat
echo   python convert.py
echo.
pause
