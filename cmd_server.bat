@echo off

set CMD=python
set MAIN=%~dp0\server\main.py
set SHELL=ConEmu64.exe

where %SHELL%
if "%ERRORLEVEL%" == "0" (
	start %SHELL%^
		"%CMD% -B %MAIN% 1000 1"^
		"%CMD% -B %MAIN% 1000 2"^
		"%CMD% -B %MAIN% 1000 3"

) else (
	start %CMD% -B %MAIN% 1000 1
	start %CMD% -B %MAIN% 1000 2
	start %CMD% -B %MAIN% 1000 3
)

REM pause
exit