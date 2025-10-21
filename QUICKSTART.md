# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Install Firefox & geckodriver

**macOS:**
```bash
brew install --cask firefox
brew install geckodriver
```

**Windows:**
- Download Firefox: https://www.mozilla.org/firefox/
- Download geckodriver: https://github.com/mozilla/geckodriver/releases
- Extract geckodriver.exe to a folder in your PATH

**Verify installation:**
```bash
geckodriver --version
```

## Step 3: Set Up Credentials

```bash
# Copy template
cp .env.template .env

# Edit .env and add your credentials
```

**macOS/Linux:**
```bash
nano .env
```

**Windows:**
```cmd
notepad .env
```

**Your .env should look EXACTLY like this:**
```
SSCS_USER=your_actual_username
SSCS_PASS=your_actual_password
```

**IMPORTANT:**
- No quotes around values
- No spaces around the `=` sign
- Replace with your actual SSCS credentials

**Verify your .env format:**
```bash
python check_env.py
```

## Step 4: Add Your Tracker File

Place `Weekly Tracker.xlsx` in the SSCS folder (same folder as main.py).

## Step 5: Test Configuration

```bash
python test_week_calc.py
```

This will verify:
- ✓ Week calculation works
- ✓ config.yaml is valid
- ✓ .env has credentials
- ✓ Excel file found

## Step 6: Test Run (Manual)

**Option A: Command line**
```bash
# With visible browser (recommended for first run)
HEADLESS=false python main.py
```

**Option B: Batch file (Windows)**
```cmd
run_sscs_update.bat
```

**Option C: Shell script (macOS/Linux)**
```bash
./run_sscs_update.sh
```

## Step 7: Check Results

After the run completes:

1. **Check logs:**
   - Open `logs/` folder
   - Review the latest log file
   - Verify "UPDATE COMPLETED SUCCESSFULLY"

2. **Check Excel:**
   - Open `Weekly Tracker.xlsx`
   - Check "Gallons v Last Year" tab
   - New week should be above "Total" row
   - Verify diesel, regular, DEF, and total values

3. **Check backups:**
   - Open `backups/` folder
   - Verify dated backup was created

## Step 8: Schedule (Optional)

**Windows:**
- See `SCHEDULER_SETUP.md` for detailed instructions
- Quick: Task Scheduler → Create Basic Task → Weekly Monday 7 AM

**macOS/Linux:**
```bash
# Edit crontab
crontab -e

# Add this line (Monday 7 AM)
0 7 * * 1 cd /Users/YourName/SSCS && /usr/bin/python3 main.py
```

## Common Issues

### "Module not found"
```bash
pip install -r requirements.txt
```

### "geckodriver not found"
Add geckodriver to your PATH or use full path.

### "Excel file not found"
Place `Weekly Tracker.xlsx` in the SSCS folder.

### ".env not found"
Copy `.env.template` to `.env` and add credentials.

### "Login failed"
- Check credentials in .env
- Try with `HEADLESS=false` to see browser

## What the Script Does

1. **Calculates last full week** (Monday 00:00 - Sunday 23:59)
2. **Logs into SSCS** with your credentials
3. **Scrapes fuel data** for each ID prefix:
   - Diesel: 050 + 019
   - Regular: 001 + 002 + 003
   - DEF: 062
4. **Updates Excel**:
   - Creates backup
   - Inserts new row above "Total"
   - Hides oldest row
   - Writes fuel data
5. **Creates log** with full details

## Files Overview

| File | Purpose |
|------|---------|
| `main.py` | Main script to run |
| `config.yaml` | Configuration (site codes, columns) |
| `.env` | Your credentials (not tracked) |
| `Weekly Tracker.xlsx` | Your tracker file |
| `test_week_calc.py` | Test configuration |
| `run_sscs_update.bat` | Windows quick-run |
| `run_sscs_update.sh` | macOS/Linux quick-run |
| `requirements.txt` | Python dependencies |
| `README.md` | Full documentation |
| `SCHEDULER_SETUP.md` | Scheduling guide |

## Support Checklist

Before asking for help:
- [ ] Ran `python test_week_calc.py` - all checks passed
- [ ] Ran `HEADLESS=false python main.py` - saw what happened
- [ ] Checked latest log file in `logs/` folder
- [ ] Verified .env has correct credentials
- [ ] Excel file is in correct location
- [ ] Python dependencies installed

## Next Steps

✓ Script working manually → Set up scheduling
✓ Monitor logs for first few runs
✓ Keep backups enabled
✓ Review data accuracy weekly

---

**Ready to go?** Run `python test_week_calc.py` then `python main.py`!
