@echo off

rem You can make a shortcut of this file and then place it on your Desktop to run it easily
rem by right clicking on this file, choosing "Create shortcut", and then dragging
rem the shortcut to your desktop

python -m puppy
if errorlevel 1 (
    pause
)
