@echo off
start cmd /k "index.html && exit"
cd ..\
call .\Linguify_env\Scripts\activate.bat
.\Linguify_env\Scripts\python.exe GestureTraining\app.py
cmd