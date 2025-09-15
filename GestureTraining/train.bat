@echo off
cd ..\
call .\Linguify_env\Scripts\activate.bat
.\Linguify_env\Scripts\python.exe GestureTraining\train.py
cmd