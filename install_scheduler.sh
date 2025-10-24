#!/bin/bash

echo "========================================"
echo "SSCS Weekly Report Scheduler Installation"
echo "========================================"
echo ""
echo "This will run the report ONCE PER WEEK"
echo "whenever you turn on your computer."
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p exports
mkdir -p backups

# Check if plist file exists
if [ ! -f "com.sscs.weeklyreport.plist" ]; then
    echo "ERROR: com.sscs.weeklyreport.plist not found!"
    exit 1
fi

# Unload existing job if it exists
echo ""
echo "Checking for existing scheduler..."
if launchctl list | grep -q "com.sscs.weeklyreport"; then
    echo "Unloading existing scheduler..."
    launchctl unload ~/Library/LaunchAgents/com.sscs.weeklyreport.plist 2>/dev/null
fi

# Copy plist to LaunchAgents
echo ""
echo "Installing scheduler..."
cp com.sscs.weeklyreport.plist ~/Library/LaunchAgents/

# Load the job
echo "Loading scheduler..."
launchctl load ~/Library/LaunchAgents/com.sscs.weeklyreport.plist

# Verify installation
echo ""
echo "Verifying installation..."
if launchctl list | grep -q "com.sscs.weeklyreport"; then
    echo "✓ Scheduler installed successfully!"
    echo ""
    echo "HOW IT WORKS:"
    echo "  - Runs ONCE PER WEEK when you log in"
    echo "  - Checks if report already ran this week"
    echo "  - If not, runs the report automatically"
    echo "  - If yes, skips until next week"
    echo ""
    echo "EXAMPLES:"
    echo "  Monday login → Runs report"
    echo "  Tuesday login → Skips (already ran)"
    echo "  Computer off all week, Friday login → Runs report"
    echo ""
    echo "To test immediately:"
    echo "  launchctl start com.sscs.weeklyreport"
    echo ""
    echo "To check if it ran this week:"
    echo "  cat .last_report_run"
    echo ""
    echo "To view wrapper logs:"
    echo "  tail -f logs/wrapper.log"
    echo ""
    echo "To force run this week again (testing):"
    echo "  rm .last_report_run"
    echo "  launchctl start com.sscs.weeklyreport"
    echo ""
    echo "To uninstall:"
    echo "  launchctl unload ~/Library/LaunchAgents/com.sscs.weeklyreport.plist"
    echo "  rm ~/Library/LaunchAgents/com.sscs.weeklyreport.plist"
else
    echo "✗ Installation failed!"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check the plist file syntax"
    echo "  2. View system logs: log show --predicate 'process == \"launchd\"' --last 1h"
    exit 1
fi

echo ""
echo "========================================"
echo "IMPORTANT: Configure your email credentials in .env file!"
echo "Edit .env and set:"
echo "  EMAIL_USER=your-email@outlook.com"
echo "  EMAIL_PASSWORD=your-password"
echo "  EMAIL_TO=recipient@example.com"
echo "========================================"
