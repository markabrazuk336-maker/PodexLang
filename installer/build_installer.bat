@echo off
REM Build PodexLang Windows installer with Inno Setup 6
setlocal EnableExtensions
cd /d "%~dp0\.."

set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
  echo ERROR: Inno Setup 6 not found. Install it, then re-run.
  exit /b 1
)

REM Ensure MinGW on PATH for rebuild if needed
set "MINGW=%LocalAppData%\Microsoft\WinGet\Packages\BrechtSanders.WinLibs.POSIX.MSVCRT.LLVM_Microsoft.Winget.Source_8wekyb3d8bbwe\mingw64\bin"
if exist "%MINGW%\g++.exe" set "PATH=%MINGW%;%PATH%"

if not exist "build\podexc.exe" (
  echo Building podexc.exe ...
  cmake -S . -B build -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=g++
  cmake --build build -j 4
)
if not exist "build\podexc.exe" (
  echo ERROR: build\podexc.exe missing
  exit /b 1
)

if not exist "installer\icons\podex.ico" (
  echo ERROR: installer\icons\podex.ico missing
  exit /b 1
)

echo Compiling installer with:
echo   "%ISCC%"
"%ISCC%" "installer\PodexLang.iss"
if errorlevel 1 exit /b 1

echo.
echo OK: dist\PodexLang-Setup-0.2.4.exe
dir /b dist\PodexLang-Setup-*.exe
endlocal
