@echo off
cd %~dp0

python main.py

if %ERRORLEVEL% == 0 (
	exit /b 0
) else (
	exit /b 1
)

@echo on
