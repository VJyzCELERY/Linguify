@echo off
cd /d %~dp0
if not exist Linguify-env\Scripts\pip-script.py (
    echo InstallingApp
    InstallWithGPU-Conda.bat
) else (
    start cmd /k "cd ./webapp && index.html && exit"
    call conda activate ./Linguify-env
    python.exe ./webapp/server.py
    cmd
)

