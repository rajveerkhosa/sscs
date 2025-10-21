#!/bin/bash
# SSCS Weekly Tracker Update - macOS/Linux Shell Script
# Run this to update the tracker manually

cd "$(dirname "$0")"

echo "============================================================"
echo "SSCS Weekly Tracker Update"
echo "============================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    echo "Please install Python 3"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found"
    echo "Please copy .env.template to .env and add your credentials"
    exit 1
fi

# Check if Weekly Tracker exists
if [ ! -f "Weekly Tracker.xlsx" ]; then
    echo "ERROR: Weekly Tracker.xlsx not found"
    echo "Please place your tracker file in this folder"
    exit 1
fi

echo "Starting update..."
echo ""

# Run the main script
python3 main.py

echo ""
echo "============================================================"
echo "Update completed. Check logs folder for details."
echo "============================================================"
echo ""
