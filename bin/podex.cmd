@echo off
REM PodexCLI entry point (also available as: podex)
setlocal EnableExtensions
set "HERE=%~dp0"
set "ROOT=%HERE%.."
if exist "%HERE%podexc.exe" set "ROOT=%HERE%.."
if exist "%HERE%..\studio\podex_cli.py" set "ROOT=%HERE%.."
if exist "%HERE%studio\podex_cli.py" set "ROOT=%HERE%"

REM Normalize ROOT
pushd "%ROOT%" >nul
set "ROOT=%CD%"
popd >nul

set "PODEX_ROOT=%ROOT%"
set "PATH=%ROOT%\bin;%ROOT%\build;%PATH%"

set "PY="
where python >nul 2>&1 && for /f "delims=" %%I in ('where python') do (set "PY=%%I" & goto :run)
if exist "%LocalAppData%\Programs\Python\Python313\python.exe" set "PY=%LocalAppData%\Programs\Python\Python313\python.exe" & goto :run
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PY=%LocalAppData%\Programs\Python\Python312\python.exe" & goto :run
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PY=%LocalAppData%\Programs\Python\Python311\python.exe" & goto :run

echo PodexCLI: Python not found. Install Python 3 and add it to PATH.
exit /b 1

:run
"%PY%" "%ROOT%\studio\podex_cli.py" %*
exit /b %ERRORLEVEL%
