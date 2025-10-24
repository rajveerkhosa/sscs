# How the Weekly Report System Works

## Simple Explanation

**The system sends you ONE email report per week, no matter when you turn on your computer.**

## How It Decides When to Run

The system uses **ISO week numbers** (Monday = start of week):
- Week 1: Jan 1-7, 2025
- Week 2: Jan 8-14, 2025
- Week 52: Dec 22-28, 2025

Every time you log in to your Mac, the system:
1. Checks what week it is (e.g., "2025-W39")
2. Looks at `.last_report_run` file to see when it last ran
3. If it's a NEW week → Runs the report
4. If it's the SAME week → Skips

## Real-World Examples

### Example 1: Normal Week
```
Monday, Sep 22, 9 AM - You log in
  → Current week: 2025-W39
  → Last run: 2025-W38 (last week)
  → ACTION: Run report! ✓
  → Saves: 2025-W39 to .last_report_run

Tuesday, Sep 23, 2 PM - You log in
  → Current week: 2025-W39
  → Last run: 2025-W39 (this week)
  → ACTION: Skip (already ran this week)

Friday, Sep 26, 10 AM - You log in
  → Current week: 2025-W39
  → Last run: 2025-W39 (this week)
  → ACTION: Skip (already ran this week)
```

### Example 2: Computer Off All Week
```
Computer off Monday-Thursday

Friday, Sep 26, 4 PM - You turn on computer
  → Current week: 2025-W39
  → Last run: 2025-W38 (last week)
  → ACTION: Run report! ✓
  → Sends you the weekly report for Sep 22-28

Saturday, Sep 27 - You restart
  → Current week: 2025-W39
  → Last run: 2025-W39 (this week)
  → ACTION: Skip (already ran Friday)
```

### Example 3: Vacation Week
```
Gone on vacation all of Week 39 (Sep 22-28)
Computer never turned on

Monday, Sep 29, 9 AM - You return and log in
  → Current week: 2025-W40 (new week!)
  → Last run: 2025-W38 (2 weeks ago)
  → ACTION: Run report! ✓
  → Sends you the report for Sep 29-Oct 5 (current week)

NOTE: You won't get the missed week (Sep 22-28) automatically.
      Run manually if you want it: python weekly_report.py
```

## What Data Gets Collected?

The report always collects data for **the most recent complete Monday-Sunday week**:

```
Today is: Friday, Sep 26, 2025
Report collects: Sep 22-28, 2025 (this week, Mon-Sun)
Compares to: Sep 23-29, 2024 (last year, same week)
```

The `week_utils.py` file calculates which Monday-Sunday period to use.

## Files the System Uses

1. **`.last_report_run`** (auto-created)
   - Stores: `2025-W39` (the week it last ran)
   - Location: `/Users/raj/SSCS/.last_report_run`
   - Used by wrapper to decide if report is needed

2. **`logs/wrapper.log`**
   - Records every time the wrapper runs
   - Shows: "Skipped" or "Running report"
   - Useful for troubleshooting

3. **`logs/weekly_report_*.log`**
   - Full logs from actual report runs
   - Created each time the report executes

## Commands

### Check if it ran this week
```bash
cat .last_report_run
# Shows: 2025-W39
```

### Force it to run again (testing)
```bash
rm .last_report_run
launchctl start com.sscs.weeklyreport
```

### View wrapper decisions
```bash
tail -20 logs/wrapper.log
```

### Manually run for a specific week
```bash
# The wrapper just calls this:
python weekly_report.py
```

## Troubleshooting

### "I didn't get a report this week"

Check:
```bash
# 1. Did the wrapper run?
tail -20 logs/wrapper.log

# 2. What week does it think it last ran?
cat .last_report_run

# 3. What week is it now?
date +%Y-W%V
```

### "I want to get last week's missed report"

```bash
# Run manually - it will collect current week's data
python weekly_report.py

# Or edit the script to specify a date range
```

### "It keeps running every day"

Check:
```bash
# Is the marker file being created?
ls -la .last_report_run

# Can the wrapper write to this directory?
ls -ld /Users/raj/SSCS
```

## When You Travel Across Time Zones

ISO week numbers are based on **local date/time**. If you travel:
- The system uses your Mac's current date
- Week boundaries may shift slightly
- Generally not an issue for business data

## Summary

✓ **You get one report per week**
✓ **Runs whenever you first log in that week**
✓ **Skips if already ran this week**
✓ **Works even if computer is off for days**
✓ **No manual intervention needed**

Just turn on your computer sometime during the week, and you'll get your report!
