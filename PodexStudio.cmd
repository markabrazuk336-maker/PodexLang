@echo off
REM Podex Studio launcher (console-friendly)
setlocal EnableExtensions
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"

set "PY="
where pythonw >nul 2>&1 && for /f "delims=" %%I in ('where pythonw') do (
  set "PY=%%I"
  goto :found
)
where python >nul 2>&1 && for /f "delims=" %%I in ('where python') do (
  set "PY=%%I"
  goto :found
)

REM Common install locations
if exist "%LocalAppData%\Programs\Python\Python311\pythonw.exe" set "PY=%LocalAppData%\Programs\Python\Python311\pythonw.exe" & goto :found
if exist "%LocalAppData%\Programs\Python\Python312\pythonw.exe" set "PY=%LocalAppData%\Programs\Python\Python312\pythonw.exe" & goto :found
if exist "%LocalAppData%\Programs\Python\Python313\pythonw.exe" set "PY=%LocalAppData%\Programs\Python\Python313\pythonw.exe" & goto :found
if exist "%ProgramFiles%\Python311\pythonw.exe" set "PY=%ProgramFiles%\Python311\pythonw.exe" & goto :found

echo Podex Studio: Python not found.
echo Install Python 3 from https://www.python.org/ and tick "Add to PATH".
pause
exit /b 1

:found
set "PATH=%ROOT%\bin;%ROOT%\build;%PATH%"
set "PODEX_ROOT=%ROOT%"
start "" "%PY%" "%ROOT%\studio\app.py" %*
endlocal
