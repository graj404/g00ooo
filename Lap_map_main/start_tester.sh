#!/bin/bash
# Quick start script for hardware testing server

echo "=========================================="
echo "Dead Reckoning Hardware Testing Server"
echo "=========================================="
echo ""
echo "Starting server on http://127.0.0.1:8888"
echo ""
echo "Available interfaces:"
echo "  - Main Dashboard: http://127.0.0.1:8888"
echo "  - 5\" Display:     http://127.0.0.1:8888/display"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

python3 web_tester.py
