@echo off
REM DeepSeek Annual Summary Frontend Launcher
REM This script starts the Flask server for the annual summary tool

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo DeepSeek Annual Summary Tool
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python found: %PYTHON_VERSION%

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM Check if deepseek.py exists
if not exist "deepseek.py" (
    echo Error: deepseek.py not found in %CD%
    echo Make sure this script is in the GPT-Rewind directory.
    pause
    exit /b 1
)

echo Project files found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install required packages
echo.
echo Installing required packages...
pip install -q flask flask-cors --upgrade

REM Check if requirements.txt exists
if exist "requirements.txt" (
    echo Installing project dependencies...
    pip install -q -r requirements.txt
)

REM Start the server
echo.
echo ===============================================
echo Starting DeepSeek Annual Summary Server
echo ===============================================
echo.
echo Server starting at http://localhost:5000
echo Open your browser and navigate to the URL above
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask app
python deepseek.py

pause
