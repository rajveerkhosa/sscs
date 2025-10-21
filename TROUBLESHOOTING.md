# Troubleshooting Guide

## Login Issues

### "Login page did not load in time"

**Symptoms:**
- `TimeoutException` error
- Script can't find username field
- Times out after 30 seconds

**Fixes:**

1. **Check your .env file format:**
   ```bash
   python check_env.py
   ```

   Your `.env` should look EXACTLY like this:
   ```
   SSCS_USER=your_username
   SSCS_PASS=your_password
   ```

   Common mistakes:
   - ✗ `SSCS_USER="john.doe"` (has quotes)
   - ✗ `SSCS_USER = john.doe` (has spaces)
   - ✗ `SSCS_USER='john.doe'` (has quotes)
   - ✓ `SSCS_USER=john.doe` (correct!)

2. **Run with visible browser to see what's happening:**
   ```bash
   HEADLESS=false python main.py
   ```

   Watch what the browser does:
   - Does the login page load?
   - Are credentials being entered?
   - Any error messages on the page?

3. **Check network/SSCS availability:**
   - Can you access SSCS manually in a browser?
   - Is your internet working?
   - Is SSCS site up?

---

### "Still on login page after submit"

**Symptoms:**
- Browser enters credentials
- Clicks login
- But stays on login page
- Warning: "Login may have failed"

**Fixes:**

1. **Verify credentials are correct:**
   ```bash
   python check_env.py
   ```

   Then manually test:
   - Open Firefox
   - Go to SSCS login page
   - Enter same username/password from .env
   - Verify they work

2. **Check for error messages on login page:**
   ```bash
   HEADLESS=false python main.py
   ```

   Look for:
   - "Invalid username or password"
   - "Account locked"
   - Any red error text

3. **Verify .env credentials don't have extra characters:**
   ```bash
   cat .env
   ```

   Check for:
   - Hidden spaces at end of lines
   - Copy/paste errors
   - Wrong username/password

---

### Login fields not found

**Symptoms:**
- Error about username/password field not found
- NoSuchElementException

**Fix:**

The script now uses `name="username"` and `name="password"`. If SSCS changed their login form, you may need to inspect the page again.

1. **Run with visible browser:**
   ```bash
   HEADLESS=false python main.py
   ```

2. **Inspect the login fields:**
   - Right-click username field → Inspect
   - Check the `name` attribute
   - If different, update `sscs_scraper.py` line 77 and 84

---

## Data Scraping Issues

### "Qty column not found"

**Symptoms:**
- Error: "Qty column not found in table headers"
- Script fails after login

**Fixes:**

1. **Check if SSCS table structure changed:**
   ```bash
   HEADLESS=false python main.py
   ```

   Look at the Transaction Line Items table:
   - Is there a "Qty" column?
   - Is it spelled differently? ("Quantity", "QTY", etc.)

2. **Check the department/site filters:**
   - Verify site code in `config.yaml` is correct
   - Department should be "1" for fuel

---

### "Footer row not found"

**Symptoms:**
- Error extracting footer value
- Can find Qty column but not the total

**Fix:**

1. **Run with visible browser and check table:**
   ```bash
   HEADLESS=false python main.py
   ```

   Look for:
   - Is there a footer row with totals?
   - Is it in `<tfoot>` or summary row?
   - Are there any rows at all?

2. **Check date range:**
   - Script uses last full week
   - If no data in that week, table might be empty
   - Check logs for the date range used

---

## Excel Update Issues

### "Total row not found"

**Symptoms:**
- Error: "Total row not found in sheet"
- Script scraped data but can't update Excel

**Fix:**

1. **Check your Excel file:**
   - Open `Weekly Tracker.xlsx`
   - Go to "Gallons v Last Year" tab
   - Is there a row with "Total" in column A?
   - Spelling must be exact: "Total" (capital T)

2. **Verify sheet names match config:**
   ```bash
   # Check config.yaml
   cat config.yaml | grep "name:"
   ```

   Sheet names must match exactly (case-sensitive):
   - "Gallons v Last Year"
   - "C Store Sales v Last Year"

---

### Excel formatting broken

**Symptoms:**
- Data written but formulas broken
- Borders missing
- Wrong number format

**Fix:**

1. **Restore from backup:**
   ```bash
   # Find your backup
   ls -lt backups/

   # Copy backup to restore
   cp backups/Weekly\ Tracker_YYYY-MM-DD.xlsx "Weekly Tracker.xlsx"
   ```

2. **Check column mappings in config.yaml:**
   - Verify columns B, E, H, K are correct
   - Match your actual Excel layout

---

## General Troubleshooting

### "Module not found"

**Error:** `ModuleNotFoundError: No module named 'selenium'`

**Fix:**
```bash
pip install -r requirements.txt
```

---

### "geckodriver not found"

**Error:** `selenium.common.exceptions.WebDriverException: 'geckodriver' executable needs to be in PATH`

**Fix:**

**macOS:**
```bash
brew install geckodriver
```

**Windows:**
1. Download: https://github.com/mozilla/geckodriver/releases
2. Extract `geckodriver.exe`
3. Add to PATH or place in Python Scripts folder

**Verify:**
```bash
geckodriver --version
```

---

### "Firefox not found"

**Fix:**

**macOS:**
```bash
brew install --cask firefox
```

**Windows:**
- Download from: https://www.mozilla.org/firefox/
- Install normally

---

### Script runs but nothing happens

**Symptoms:**
- No errors
- But Excel not updated
- No data collected

**Fixes:**

1. **Check the log file:**
   ```bash
   # Find latest log
   ls -lt logs/

   # Read it
   cat logs/sscs_update_YYYY-MM-DD_HH-MM-SS.log
   ```

2. **Verify Weekly Tracker.xlsx exists:**
   ```bash
   ls -l "Weekly Tracker.xlsx"
   ```

3. **Check if Excel is open:**
   - Close Excel completely
   - Run script again

---

## Running with Visible Browser (Best for Debugging)

**Always use this when troubleshooting:**

```bash
HEADLESS=false python main.py
```

**On Windows:**
```cmd
set HEADLESS=false
python main.py
```

This lets you:
- See the browser in action
- Watch login process
- See if errors appear on page
- Verify data is being scraped

---

## Quick Diagnostic Checklist

Before asking for help, verify:

- [ ] Ran `python check_env.py` - passes all checks
- [ ] Ran `python test_week_calc.py` - all tests pass
- [ ] Ran `HEADLESS=false python main.py` - watched what happened
- [ ] Checked latest log in `logs/` folder
- [ ] Verified credentials work manually in browser
- [ ] `Weekly Tracker.xlsx` exists in correct location
- [ ] Excel file has "Total" row in column A
- [ ] Firefox and geckodriver installed and working

---

## Common Error Messages

| Error | Likely Cause | Fix |
|-------|--------------|-----|
| `TimeoutException` at login | .env not set up or wrong format | Run `check_env.py` |
| "Still on login page" | Wrong credentials | Verify credentials manually |
| "Qty column not found" | SSCS table changed or no data | Check with visible browser |
| "Total row not found" | Excel structure doesn't match | Check Excel file has "Total" in column A |
| "Module not found" | Dependencies not installed | `pip install -r requirements.txt` |
| "geckodriver not found" | WebDriver not in PATH | Install geckodriver |

---

## Getting Help

1. **Run diagnostics:**
   ```bash
   python check_env.py
   python test_week_calc.py
   ```

2. **Run with visible browser:**
   ```bash
   HEADLESS=false python main.py
   ```

3. **Check the log file:**
   ```bash
   cat logs/sscs_update_*.log
   ```

4. **Share:**
   - Error message from terminal
   - Relevant lines from log file
   - What you saw in visible browser mode
   - Results of `check_env.py` and `test_week_calc.py`

---

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Login fails | `python check_env.py` |
| Can't see what's wrong | `HEADLESS=false python main.py` |
| Dependencies missing | `pip install -r requirements.txt` |
| Excel not updating | Check for "Total" row in column A |
| Wrong data | Verify date range in logs |
| Credentials wrong | `nano .env` (edit and save) |

---

## Prevention

**Best practices to avoid issues:**

1. **Always test .env first:**
   ```bash
   python check_env.py
   ```

2. **Run with visible browser for first time:**
   ```bash
   HEADLESS=false python main.py
   ```

3. **Check logs after every run:**
   ```bash
   ls -lt logs/ | head -5
   ```

4. **Keep backups:**
   - Backups are automatic in `backups/` folder
   - Don't delete them!

5. **Monitor weekly (first month):**
   - Check data accuracy
   - Compare to SSCS manually
   - Verify formulas working

---

**Still stuck?** Share your error message and the output of `check_env.py` and `test_week_calc.py`.
