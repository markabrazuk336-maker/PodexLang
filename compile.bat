@echo off
REM Build podexc then compile a .pdx file to an .exe (MinGW)
setlocal
set MINGW=C:\Users\Markazuk\AppData\Local\Microsoft\WinGet\Packages\BrechtSanders.WinLibs.POSIX.MSVCRT.LLVM_Microsoft.Winget.Source_8wekyb3d8bbwe\mingw64\bin
set PATH=%MINGW%;%PATH%

if not exist build\podexc.exe (
  cmake -S . -B build -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=g++
  cmake --build build -j 4
)

if "%~1"=="" (
  echo Usage: compile.bat examples\hello.pdx
  exit /b 1
)

set SRC=%~1
set NAME=%~n1
build\podexc.exe "%SRC%" -o "build\%NAME%.cpp"
if errorlevel 1 exit /b 1
g++ -std=c++17 -O2 -finput-charset=UTF-8 -fexec-charset=UTF-8 "build\%NAME%.cpp" -o "build\%NAME%.exe"
if errorlevel 1 exit /b 1
echo Built build\%NAME%.exe
endlocal
