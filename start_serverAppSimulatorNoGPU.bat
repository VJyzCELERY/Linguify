@echo off
cd /d %~dp0
if not exist Linguify_env\Scripts\python.exe (
    echo InstallingApp
    InstallWithGPU.bat
) else (
    start cmd /k "cd ./appsimulator && index.html && exit"
    call Linguify_env\Scripts\activate.bat
    .\Linguify_env\Scripts\python.exe ./appsimulator/serverNoGPU.py
    cmd
)

