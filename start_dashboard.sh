#!/bin/bash
# Start the AI Content Automation Dashboard

echo "========================================"
echo "AI Content Automation Dashboard"
echo "========================================"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Flask not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the dashboard
echo ""
echo "Starting dashboard server..."
echo "Dashboard will be available at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

python dashboard/app.py
