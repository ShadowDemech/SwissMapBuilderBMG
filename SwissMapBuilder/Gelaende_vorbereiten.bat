@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto error
)
.venv\Scripts\python.exe -m pip install -e .
if errorlevel 1 goto error
.venv\Scripts\python.exe -m swissmapbuilder prepare
if errorlevel 1 goto error
echo.
echo Gelaende erfolgreich vorbereitet. Noch kein spielbarer BeamNG-Level.
pause
exit /b 0
:error
echo.
echo Verarbeitung fehlgeschlagen. Bitte die Fehlermeldung oberhalb kopieren.
pause
exit /b 1
