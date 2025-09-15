@echo off
cd /d %~dp0

REM Log start of script
echo [%date% %time%] Starting GPU installation process...

REM Check if Conda is installed
where conda >nul 2>nul
if "%errorlevel%" neq "0" (
    echo [%date% %time%] Conda is not installed. Please install Anaconda or Miniconda first.
    pause
    exit /b
)

REM Ensure the venv directory exists and create it if necessary
if not exist Linguify-env\Scripts\pip-script.py (
    echo [%date% %time%] Creating Conda environment...
    conda create --prefix ./Linguify-env python=3.12 -y
    conda activate ./Linguify-env
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
    pip install -r requirements-gpu.txt
) else (
    echo [%date% %time%] Conda environment already exists.
)