# Windows Task Scheduler Setup Guide

## Quick Setup (GUI Method)

1. **Open Task Scheduler**
   - Press `Win + R`
   - Type `taskschd.msc`
   - Press Enter

2. **Create New Task**
   - Click "Create Basic Task..." in right panel
   - Name: `SSCS Weekly Update`
   - Description: `Automated SSCS fuel data scraper and Excel updater`
   - Click Next

3. **Set Trigger**
   - Select "Weekly"
   - Click Next
   - Start date: (today or next Monday)
   - Start time: `7:00 AM`
   - Recur every: `1 weeks`
   - Check: `Monday`
   - Click Next

4. **Set Action**
   - Select "Start a program"
   - Click Next

5. **Configure Program**
   - **Program/script:** (Choose one)
     - If Python in PATH: `python`
     - If not: Full path like `C:\Python39\python.exe`

   - **Add arguments:** `main.py`

   - **Start in:** Full path to your SSCS folder
     - Example: `C:\Users\YourName\Documents\SSCS`
     - **IMPORTANT:** This must be the directory containing main.py

   - Click Next

6. **Finish**
   - Check "Open the Properties dialog..."
   - Click Finish

7. **Additional Settings (in Properties)**
   - Go to "Conditions" tab:
     - Uncheck "Start only if on AC power"
     - Check "Wake the computer to run this task" (optional)

   - Go to "Settings" tab:
     - Check "Run task as soon as possible after scheduled start is missed"
     - Set "Stop the task if it runs longer than:" to `1 hour`

   - Click OK

## Verification

### Test the Task Immediately

1. In Task Scheduler, find your task in the list
2. Right-click → "Run"
3. Watch for the task to complete
4. Check the "Last Run Result" column
   - `0x0` = Success
   - Other codes = Error (check logs)

### Check Logs

After running, verify:
- New log file in `SSCS/logs/` folder
- Backup created in `SSCS/backups/` folder
- Excel updated with new week data

## Troubleshooting

### Task shows "Running" but nothing happens

**Cause:** Working directory not set correctly

**Fix:**
1. Edit the task
2. Go to "Actions" tab
3. Edit the action
4. Make sure "Start in" field has your SSCS folder path

### Error: "The system cannot find the file specified"

**Cause:** Python path incorrect or main.py not found

**Fix:**
1. Find your Python path:
   ```cmd
   where python
   ```
2. Edit task action:
   - Program: Use full path from `where python`
   - Arguments: `main.py`
   - Start in: Your SSCS folder

### Error: "No module named 'selenium'" (or other modules)

**Cause:** Wrong Python environment or packages not installed

**Fix:**
1. Open CMD in your SSCS folder
2. Check which Python the task uses:
   ```cmd
   where python
   ```
3. Install requirements with that Python:
   ```cmd
   C:\Python39\python.exe -m pip install -r requirements.txt
   ```

### Task runs but Excel not updated

**Check:**
1. Log file in `logs/` folder for error details
2. Excel file is not open when task runs
3. Excel file path in config.yaml is correct
4. .env file exists with valid credentials

### Want to see the browser window

**Option 1:** Run task manually with visible browser
1. Open CMD in SSCS folder
2. Run:
   ```cmd
   set HEADLESS=false
   python main.py
   ```

**Option 2:** Modify scheduled task
1. Edit task
2. Actions → Edit
3. Arguments: Change to `-c "import os; os.environ['HEADLESS']='false'; exec(open('main.py').read())"`
4. Program: `python`

## Advanced: XML Import Method

If you prefer to use an XML file:

1. Create `sscs_task.xml` (see README.md for template)

2. **Edit these paths in the XML:**
   - Line with `<Command>`: Your Python path
   - Line with `<WorkingDirectory>`: Your SSCS folder path
   - Line with `<StartBoundary>`: Adjust start date if needed

3. **Import the task:**
   ```powershell
   schtasks /create /tn "SSCS Weekly Update" /xml sscs_task.xml /ru %USERNAME%
   ```

4. **Verify:**
   ```powershell
   schtasks /query /tn "SSCS Weekly Update" /v
   ```

## Monitoring

### View Task History

1. In Task Scheduler, select your task
2. Click "History" tab at bottom
3. Review events (start, success, errors)

### Email Notifications (Optional)

1. Edit task → Actions tab
2. Add new action: "Send an e-mail"
3. Configure SMTP settings
4. Set to trigger on success or failure

**Note:** Email action is deprecated in newer Windows versions. Consider using a script to send emails instead.

## Disabling/Enabling the Task

**Disable:**
- Right-click task → Disable

**Enable:**
- Right-click task → Enable

**Delete:**
- Right-click task → Delete

## Best Practices

1. **Test First:** Run task manually before scheduling
2. **Check Logs:** Review logs after first scheduled run
3. **Monitor:** Check weekly for first month to ensure reliability
4. **Backup:** Keep Excel backups (automatically created)
5. **Credentials:** Ensure .env file has correct credentials
6. **Network:** Task requires internet to access SSCS

## Alternative: Manual Batch File

If you prefer a double-click solution instead of scheduling:

Create `run_sscs_update.bat` in your SSCS folder:

```batch
@echo off
cd /d "%~dp0"
echo SSCS Weekly Tracker Update
echo ========================
echo.

python main.py

echo.
echo ========================
echo Press any key to close...
pause > nul
```

Then:
- Double-click `run_sscs_update.bat` to run manually
- Or schedule this .bat file in Task Scheduler instead

## macOS Alternative (Bonus)

If using macOS, use launchd instead:

1. Create `~/Library/LaunchAgents/com.sscs.weekly.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sscs.weekly</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/YourName/SSCS/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/YourName/SSCS</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>7</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/YourName/SSCS/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YourName/SSCS/logs/launchd_error.log</string>
</dict>
</plist>
```

2. Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.sscs.weekly.plist
```

## Summary

- ✅ Schedule for Monday 7:00 AM weekly
- ✅ Set working directory to SSCS folder
- ✅ Test manually before relying on schedule
- ✅ Monitor logs for first few runs
- ✅ Keep backups enabled
