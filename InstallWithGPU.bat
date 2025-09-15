@echo off
cd /d %~dp0

REM Check if the venv directory exists
if not exist Linguify_env\Scripts\python.exe (
    echo Creating VENV
    python -m venv Linguify_env
) else (
    echo VENV already exists
)

echo Activating VENV
PAUSE
start cmd /k "call Linguify_env\Scripts\activate.bat && install_with_gpu_support.bat"
