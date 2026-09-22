@echo off
:: parse_recording.bat - Invokes nv_parser with the specified binary file
setlocal enabledelayedexpansion

:: Get the directory where the batch file is located
set "SCRIPT_DIR=%~dp0"

if "%~1"=="" (
    echo Error: Please provide an input file
    echo Usage: %~nx0 ^<path_to_bin_file^>
    exit /b 1
)

:: Get the absolute path of the input file
set "INPUT_FILE=%~f1"

:: Run the parser
"%SCRIPT_DIR%nv_parser.exe" "%INPUT_FILE%"

if errorlevel 1 (
    echo.
    echo Parsing failed
    pause
    exit /b 1
)

echo.
exit /b 0
