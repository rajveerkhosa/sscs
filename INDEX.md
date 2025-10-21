# SSCS Weekly Tracker - Documentation Index

## Quick Access

| What do you need? | Go to... |
|-------------------|----------|
| 🚀 **Get started in 5 minutes** | [QUICKSTART.md](QUICKSTART.md) |
| 📖 **Full documentation** | [README.md](README.md) |
| ⏰ **Set up Windows scheduler** | [SCHEDULER_SETUP.md](SCHEDULER_SETUP.md) |
| 🔍 **Understand how it works** | [WORKFLOW.txt](WORKFLOW.txt) |
| 📋 **Project overview** | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |
| ⚙️ **Install everything** | Run `install.sh` or `install.bat` |
| ✅ **Test configuration** | Run `python test_week_calc.py` |
| ▶️ **Run the script** | Run `python main.py` |

---

## Documentation Files

### Getting Started

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
  - Dependencies installation
  - Credential setup
  - First run test
  - Quick troubleshooting

- **[README.md](README.md)** - Complete documentation
  - Feature overview
  - Detailed setup instructions
  - Configuration guide
  - File structure
  - How it works
  - Troubleshooting
  - Acceptance criteria

- **Installation Scripts**
  - `install.sh` - Automated setup for macOS/Linux
  - `install.bat` - Automated setup for Windows

### Understanding the System

- **[WORKFLOW.txt](WORKFLOW.txt)** - Visual workflow diagram
  - Step-by-step process flow
  - Data collection logic
  - Excel update behavior
  - Error handling
  - URL structure
  - Table scraping algorithm

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Technical overview
  - Architecture
  - Data flow
  - Configuration points
  - Key features
  - Performance metrics
  - Maintenance guide

### Scheduling

- **[SCHEDULER_SETUP.md](SCHEDULER_SETUP.md)** - Complete scheduling guide
  - Windows Task Scheduler (GUI method)
  - Windows Task Scheduler (XML method)
  - macOS launchd
  - Linux cron
  - Troubleshooting scheduled tasks
  - Monitoring task execution

---

## Code Files

### Core Scripts

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | Main orchestration script | ~190 |
| `week_utils.py` | Week calculation & date formatting | ~110 |
| `sscs_scraper.py` | Web scraping with Selenium | ~370 |
| `fuel_aggregator.py` | Fuel data aggregation logic | ~170 |
| `excel_updater.py` | Excel update with format preservation | ~360 |

### Testing & Utilities

| File | Purpose |
|------|---------|
| `test_week_calc.py` | Configuration validation script |
| `run_sscs_update.bat` | Windows quick-run wrapper |
| `run_sscs_update.sh` | macOS/Linux quick-run wrapper |

### Configuration

| File | Purpose | Track in Git? |
|------|---------|---------------|
| `config.yaml` | SSCS settings, fuel prefixes, column mappings | ✓ Yes |
| `.env` | Your credentials (username/password) | ✗ **NO** |
| `.env.template` | Template for .env file | ✓ Yes |
| `.gitignore` | Git exclusions | ✓ Yes |
| `requirements.txt` | Python dependencies | ✓ Yes |

---

## Common Tasks

### First Time Setup

1. **Install dependencies:**
   ```bash
   # macOS/Linux
   ./install.sh

   # Windows
   install.bat
   ```

2. **Configure credentials:**
   ```bash
   cp .env.template .env
   nano .env  # or notepad .env on Windows
   ```

3. **Add your tracker file:**
   - Place `Weekly Tracker.xlsx` in this folder

4. **Test:**
   ```bash
   python test_week_calc.py
   HEADLESS=false python main.py
   ```

### Regular Operations

- **Run manually:** `python main.py`
- **Run with visible browser:** `HEADLESS=false python main.py`
- **Check logs:** Look in `logs/` folder
- **Restore backup:** Copy from `backups/` folder

### Troubleshooting

1. **Read the log file** in `logs/` folder
2. **Run test script:** `python test_week_calc.py`
3. **Check with visible browser:** `HEADLESS=false python main.py`
4. **See README.md** → Troubleshooting section
5. **See SCHEDULER_SETUP.md** → Troubleshooting section (if scheduled)

---

## Configuration Reference

### Site & Credentials (config.yaml)

```yaml
sscs:
  login_url: "https://sscsta.sscsinc.com/Auth.App/#/login?..."
  base_url: "https://sscsta.sscsinc.com/TransactionAnalysis.App"
  selected_site_code: "006579001"
  credentials:
    user_env: "SSCS_USER"
    pass_env: "SSCS_PASS"
```

### Fuel Prefixes (config.yaml)

```yaml
fuel:
  department: "1"
  diesel_prefixes: ["050", "019"]
  regular_prefixes: ["001", "002", "003"]
  def_prefixes: ["062"]
```

### Excel Columns (config.yaml)

```yaml
excel:
  sheets:
    - name: "Gallons v Last Year"
      thisweek_columns:
        diesel_gal: "B"    # Diesel (This week)
        regular_gal: "E"   # Gas (This week)
        def_gal: "H"       # DEF (This week)
        total_gal: "K"     # Total (This week)
```

### Credentials (.env)

```
SSCS_USER=your_username
SSCS_PASS=your_password
```

### Environment Variables (optional)

```bash
HEADLESS=false          # Show browser
RUN_SANITY_CHECK=true   # Run pagination check
```

---

## File Structure

```
SSCS/
├── Documentation (start here!)
│   ├── INDEX.md ←────────────────── YOU ARE HERE
│   ├── QUICKSTART.md
│   ├── README.md
│   ├── SCHEDULER_SETUP.md
│   ├── PROJECT_SUMMARY.md
│   └── WORKFLOW.txt
│
├── Scripts (main functionality)
│   ├── main.py
│   ├── week_utils.py
│   ├── sscs_scraper.py
│   ├── fuel_aggregator.py
│   └── excel_updater.py
│
├── Configuration
│   ├── config.yaml
│   ├── .env (create from template)
│   └── .env.template
│
├── Utilities
│   ├── install.sh / install.bat
│   ├── test_week_calc.py
│   ├── run_sscs_update.sh / .bat
│   ├── requirements.txt
│   └── .gitignore
│
├── Data (you provide / auto-generated)
│   ├── Weekly Tracker.xlsx ←─── PLACE YOUR FILE HERE
│   ├── backups/ (auto-created)
│   ├── logs/ (auto-created)
│   └── exports/ (unused in scrape mode)
│
└── .claude/ (Claude Code settings)
```

---

## Dependencies

### Python Packages

Install with: `pip install -r requirements.txt`

- `selenium>=4.15.0` - Web automation
- `openpyxl>=3.1.2` - Excel read/write
- `python-dotenv>=1.0.0` - .env loading
- `PyYAML>=6.0.1` - YAML config

### External Software

- **Firefox** - Web browser
  - macOS: `brew install --cask firefox`
  - Windows: https://www.mozilla.org/firefox/

- **geckodriver** - Firefox WebDriver
  - macOS: `brew install geckodriver`
  - Windows: https://github.com/mozilla/geckodriver/releases

---

## Data Flow Summary

```
1. Calculate Week
   └→ Last full Sunday (Mon 00:00 - Sun 23:59)

2. Login to SSCS
   └→ Scrape Transaction Line Items for each prefix

3. Aggregate Data
   └→ Diesel = 050 + 019
   └→ Regular = 001 + 002 + 003
   └→ DEF = 062
   └→ Total = Diesel + Regular + DEF

4. Update Excel
   └→ Backup file
   └→ Insert row above "Total"
   └→ Write fuel data
   └→ Hide oldest row
   └→ Save

5. Log Results
   └→ Detailed log in logs/ folder
```

---

## Support Checklist

Before asking for help, verify:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Firefox installed
- [ ] geckodriver in PATH (`geckodriver --version`)
- [ ] `.env` file exists with credentials
- [ ] `Weekly Tracker.xlsx` in project folder
- [ ] Ran `python test_week_calc.py` - all checks passed
- [ ] Checked latest log file in `logs/` folder
- [ ] Tried with `HEADLESS=false` to see browser

---

## Quick Reference

### Run Commands

| Command | Purpose |
|---------|---------|
| `python test_week_calc.py` | Test configuration |
| `python main.py` | Run in headless mode |
| `HEADLESS=false python main.py` | Run with visible browser |
| `./run_sscs_update.sh` | Quick run (macOS/Linux) |
| `run_sscs_update.bat` | Quick run (Windows) |

### Important Paths

| Path | Contents |
|------|----------|
| `logs/` | Run logs with timestamps |
| `backups/` | Dated Excel backups |
| `.env` | Your credentials |
| `config.yaml` | SSCS and Excel settings |

### Key Files to Edit

| File | When to Edit | Why |
|------|--------------|-----|
| `.env` | Setup, credential change | Add/update credentials |
| `config.yaml` | Setup, requirements change | Change site code, prefixes, columns |
| `Weekly Tracker.xlsx` | Never (auto-updated) | Script updates this file |

---

## Acceptance Criteria

✓ **Week Calculation**
- Last full Sunday calculated correctly
- Date range: Mon 00:00 to Sun 23:59
- Label formatted as "22nd Sep"

✓ **Data Collection**
- Diesel = sum of prefixes 050 + 019
- Regular = sum of 001 + 002 + 003
- DEF = prefix 062
- Total = Diesel + Regular + DEF
- Sanity check: sum(all prefixes) == total

✓ **Excel Update**
- Backup created before update
- New row inserted above "Total"
- Week label written to column A
- Fuel values written to correct columns (B, E, H, K)
- Oldest row hidden (not deleted)
- Formatting preserved (borders, numbers, fonts)
- Formulas untouched (Last Year, % v LY)

✓ **Logging**
- Log file created with timestamp
- Contains: week label, all gallons, warnings, errors
- Success/failure clearly indicated

---

## Next Steps

1. **New user?** → Start with [QUICKSTART.md](QUICKSTART.md)
2. **Need details?** → Read [README.md](README.md)
3. **Want to schedule?** → See [SCHEDULER_SETUP.md](SCHEDULER_SETUP.md)
4. **How does it work?** → Review [WORKFLOW.txt](WORKFLOW.txt)
5. **Technical deep dive?** → Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## Version

- **Created:** October 2025
- **Version:** 1.0
- **Status:** Production Ready

---

**Questions?** Check the documentation files above or run `python test_week_calc.py` for diagnostics.
