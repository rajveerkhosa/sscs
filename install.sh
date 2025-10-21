#!/bin/bash
# SSCS Weekly Tracker - Installation Script for macOS/Linux

set -e  # Exit on error

echo "============================================================"
echo "SSCS Weekly Tracker - Installation"
echo "============================================================"
echo ""

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Check pip
echo "Checking pip..."
if ! python3 -m pip --version &> /dev/null; then
    echo "ERROR: pip not found"
    echo "Please install pip"
    exit 1
fi
echo "✓ pip found"
echo ""

# Install Python packages
echo "Installing Python packages..."
python3 -m pip install -r requirements.txt
echo "✓ Python packages installed"
echo ""

# Check Firefox
echo "Checking Firefox..."
if command -v firefox &> /dev/null; then
    echo "✓ Firefox found"
else
    echo "⚠ Firefox not found"
    echo "  Install with: brew install --cask firefox"
fi
echo ""

# Check geckodriver
echo "Checking geckodriver..."
if command -v geckodriver &> /dev/null; then
    GECKO_VERSION=$(geckodriver --version | head -n1)
    echo "✓ geckodriver found ($GECKO_VERSION)"
else
    echo "⚠ geckodriver not found"
    echo "  Install with: brew install geckodriver"
fi
echo ""

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.template .env
    echo "✓ .env created from template"
    echo "  ⚠ IMPORTANT: Edit .env and add your SSCS credentials!"
else
    echo "✓ .env already exists"
fi
echo ""

# Create directories
echo "Creating directories..."
mkdir -p exports backups logs
echo "✓ Directories created (exports, backups, logs)"
echo ""

# Check for Weekly Tracker
if [ ! -f "Weekly Tracker.xlsx" ]; then
    echo "⚠ Weekly Tracker.xlsx not found"
    echo "  Place your tracker file in this folder before running"
else
    echo "✓ Weekly Tracker.xlsx found"
fi
echo ""

# Make scripts executable
echo "Making scripts executable..."
chmod +x run_sscs_update.sh
chmod +x test_week_calc.py
chmod +x main.py
echo "✓ Scripts are now executable"
echo ""

# Test configuration
echo "Testing configuration..."
python3 test_week_calc.py
echo ""

# Summary
echo "============================================================"
echo "Installation Summary"
echo "============================================================"
echo ""
echo "Next Steps:"
echo ""
echo "1. Edit .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Place Weekly Tracker.xlsx in this folder"
echo ""
echo "3. Test the script:"
echo "   HEADLESS=false python3 main.py"
echo ""
echo "4. If test succeeds, set up scheduling:"
echo "   - macOS: See README.md for launchd setup"
echo "   - Linux: See README.md for cron setup"
echo ""
echo "============================================================"
echo "Installation complete!"
echo "============================================================"
