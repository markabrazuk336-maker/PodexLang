@echo off
cd /d "%~dp0"
if exist "%~dp0PodexStudio.cmd" (
  call "%~dp0PodexStudio.cmd" %*
) else (
  python studio\app.py %*
)
