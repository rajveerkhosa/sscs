#!/bin/bash
#
# Smart Weekly Report Wrapper
# Runs the SSCS weekly report once per week, no matter which day you turn on your computer.
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKER_FILE="$SCRIPT_DIR/.last_report_run"
LOG_DIR="$SCRIPT_DIR/logs"
PYTHON="/opt/anaconda3/bin/python3"
REPORT_SCRIPT="$SCRIPT_DIR/weekly_report.py"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/wrapper.log"
}

log "========================================"
log "Weekly Report Wrapper Started"
log "========================================"

# Get current week number (ISO week: Monday = start of week)
current_week=$(date +%Y-W%V)
log "Current week: $current_week"

# Check if marker file exists
if [ -f "$MARKER_FILE" ]; then
    last_run_week=$(cat "$MARKER_FILE")
    log "Last run week: $last_run_week"

    # Compare week numbers
    if [ "$current_week" = "$last_run_week" ]; then
        log "Report already ran this week ($current_week)"
        log "Skipping execution"
        log "========================================"
        exit 0
    else
        log "New week detected! Last run: $last_run_week, Current: $current_week"
    fi
else
    log "No previous run detected (marker file not found)"
fi

# New week or first run - execute the report
log "Running weekly report..."
log "Command: $PYTHON $REPORT_SCRIPT"
log "----------------------------------------"

# Run the report
cd "$SCRIPT_DIR" || exit 1
"$PYTHON" "$REPORT_SCRIPT"
exit_code=$?

log "----------------------------------------"
log "Report execution completed with exit code: $exit_code"

# If successful, update the marker file
if [ $exit_code -eq 0 ]; then
    echo "$current_week" > "$MARKER_FILE"
    log "✓ Marker file updated: $current_week"
    log "✓ Weekly report completed successfully"
else
    log "✗ Weekly report failed (exit code: $exit_code)"
    log "  Marker file NOT updated - will retry next login"
fi

log "========================================"
exit $exit_code
