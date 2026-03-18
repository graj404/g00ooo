#!/bin/bash
# Quick run script that handles virtual environment

if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    python main.py
else
    python3 main.py
fi
