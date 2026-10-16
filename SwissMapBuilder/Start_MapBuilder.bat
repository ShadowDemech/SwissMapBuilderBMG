@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto error
.venv\Scripts\python -m pip install -e .
if errorlevel 1 goto error
.venv\Scripts\python -m swissmapbuilder ui
pause
exit /b
:error
echo Start fehlgeschlagen. Python 3.10 oder neuer installieren und Internetverbindung pruefen.
pause
