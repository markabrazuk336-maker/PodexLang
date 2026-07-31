@echo off
REM Dev shim when bin\ is not on PATH yet — from repo root
call "%~dp0bin\podex.cmd" %*
