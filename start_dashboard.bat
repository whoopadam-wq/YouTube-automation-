@echo off
REM Start the AI Content Automation Dashboard

echo ========================================
echo AI Content Automation Dashboard
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask not found. Installing dependencies...
    pip install -r requirements.txt
)

REM Start the dashboard
echo.
echo Starting dashboard server...
echo Dashboard will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python dashboard\app.py

pause
