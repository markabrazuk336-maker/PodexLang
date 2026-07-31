@echo off
cd /d "%~dp0"
python studio\app.py %*
if errorlevel 1 (
  echo.
  echo Failed to start Podex Studio. Is Python installed?
  pause
)
