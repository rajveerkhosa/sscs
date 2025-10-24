# SSCS Weekly Data Collection & Email Automation

Automated system to collect weekly data from SSCS (fuel, C-Store sales, departments) and email formatted reports.

## 🎯 What This Does

- **Collects Data:** Scrapes fuel gallons, C-Store sales, and department sales from SSCS
- **Compares Year-over-Year:** Automatically pulls last year's data for comparison
- **Sends Weekly Emails:** Formatted reports with breakdowns and copy-paste sections for Excel
- **Runs Automatically:** Once per week when you turn on your computer (no manual intervention needed)

## 📋 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

Edit `.env` file:

```bash
# SSCS Login
SSCS_USER=your-sscs-username
SSCS_PASS=your-sscs-password

# Gmail Setup (for sending emails)
# 1. Go to: https://myaccount.google.com/apppasswords
# 2. Create an App Password for "Mail"
# 3. Copy the 16-character password (remove spaces)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_TO=recipient@gmail.com

# Browser Setting
HEADLESS=false  # Set to 'true' to run browser in background
```

### 3. Test It Works

```bash
# Quick email test (no data collection)
python test_email_only.py

# Full test with data collection
python weekly_report.py
```

### 4. Install Automatic Scheduler

```bash
./install_scheduler.sh
```

**Done!** The system will now run once per week automatically when you log in.

## 📧 What You'll Receive

Each week, you'll get an email with:

### Summary Data
- Fuel totals (Diesel, Regular, DEF) - THIS WEEK vs LAST YEAR
- C-Store sales (Total, Lottery, Scale, Other) - THIS WEEK vs LAST YEAR
- Department sales summary with top 10 departments

### Detailed Breakdowns
- **Fuel by prefix:** 050, 019, 001, 002, 003, 062
- **Lottery by department:** Dept 27, 43, 72
- **Scale:** Dept 88

### Copy-Paste Section
Ready-to-paste values for Excel:
- Weekly Gallons 25 (columns B-L)
- C Store Sales 25 (columns B-L)
- All department sales with totals

## 🗂️ Project Structure

### Core Scripts
- `weekly_report.py` - Main automation script
- `weekly_report_wrapper.sh` - Smart weekly runner (prevents duplicate runs)
- `get_all_data.py` - Manual data collection (display in terminal)
- `test_email_only.py` - Quick email test

### Data Collection Modules
- `sscs_scraper.py` - SSCS login and scraping
- `fuel_aggregator.py` - Fuel data collection
- `storestats_scraper.py` - C-Store and department scraping
- `cstore_aggregator.py` - C-Store data aggregation

### Utilities
- `email_sender.py` - Gmail email sending
- `week_utils.py` - Week calculations (Monday-Sunday)
- `excel_writer.py` - Excel generation (future feature)

### Configuration
- `config.yaml` - SSCS site codes and fuel prefixes
- `.env` - Credentials (DO NOT COMMIT!)
- `requirements.txt` - Python dependencies

### Scheduler
- `com.sscs.weeklyreport.plist` - macOS launchd configuration
- `install_scheduler.sh` - One-command installer

## 🔧 How It Works

### Weekly Automation
1. **Trigger:** Runs every time you log in
2. **Check:** Wrapper checks if report already ran this week
3. **Collect:** If new week, scrapes all SSCS data
4. **Email:** Sends formatted report to your email
5. **Mark:** Records week number to prevent duplicate runs

### Data Collection
- Uses Selenium with Firefox to automate SSCS login
- Navigates to Transaction Line Items for fuel data
- Uses Store Stats page for C-Store totals
- Scrapes individual departments from Transaction Line Items
- Retries failed requests automatically
- Handles slow WiFi with extended wait times

### Week Calculation
- Week = Monday to Sunday (ISO week)
- Excel labels = Monday AFTER week ends (e.g., Oct 13-19 → "Oct 20th")
- Last year = Same week number from previous year

## 📅 Schedule

**Default:** Runs once per week when you log in

**Examples:**
- Monday login → Runs report
- Tuesday login → Skips (already ran Monday)
- Computer off all week, Friday login → Runs immediately
- Multiple logins same week → Only runs once

### Check Status
```bash
# See if it ran this week
cat .last_report_run
# Shows: 2025-W43 (current week number)

# View wrapper log
tail -20 logs/wrapper.log
```

### Force Run Again (Testing)
```bash
rm .last_report_run
launchctl start com.sscs.weeklyreport
```

## 🛠️ Commands

### Manual Operations
```bash
# Collect all data and display in terminal
python get_all_data.py

# Run full weekly report (scrape + email)
python weekly_report.py

# Test email only (no scraping)
python test_email_only.py
```

### Scheduler Management
```bash
# Check if scheduler is running
launchctl list | grep sscs

# View logs
tail -f logs/wrapper.log
tail -f logs/weekly_report_*.log

# Uninstall scheduler
launchctl unload ~/Library/LaunchAgents/com.sscs.weeklyreport.plist
rm ~/Library/LaunchAgents/com.sscs.weeklyreport.plist
```

## 📊 Data Sources

### Fuel Data (Prefix-based)
- **Diesel:** 050, 019
- **Regular Gas:** 001, 002, 003
- **DEF:** 062

### C-Store Sales
- **Total C-Store:** Store Stats "Total Merchandise Sales"
- **Lottery:** Dept 27 + 43 + 72 (Transaction Line Items)
- **Scale:** Dept 88 (Transaction Line Items)
- **Other Sales:** Total - Lottery - Scale

### Department Sales
Reads all departments from "Weekly Department Sales.xlsx" and scrapes each one individually.

## 🔒 Security

- **Never commit `.env`** - contains passwords
- Use **Gmail App Password** instead of account password
- Enable **2-Step Verification** on Gmail
- `.gitignore` configured to exclude:
  - `.env`
  - `.claude/` and `.claude.json`
  - Excel files
  - Logs and exports
  - `.last_report_run`

## 🐛 Troubleshooting

### Email Not Sending
```bash
# Test email credentials
python test_email_only.py

# Check .env file
cat .env | grep EMAIL
```

**Common fixes:**
- Create Gmail App Password (not account password)
- Enable 2-Step Verification on Gmail first
- Remove spaces from app password

### Scheduler Not Running
```bash
# Check if loaded
launchctl list | grep sscs

# Reload
launchctl unload ~/Library/LaunchAgents/com.sscs.weeklyreport.plist
launchctl load ~/Library/LaunchAgents/com.sscs.weeklyreport.plist
```

### Browser Issues
If `HEADLESS=true` fails:
- Set `HEADLESS=false` in `.env`
- Make sure you're logged in when job runs
- Check `geckodriver` is installed: `which geckodriver`

### Data Showing $0.00
- Slow WiFi: Script already waits 12 seconds, retries 3 times
- True no data: Page shows "Nothing found" (expected)
- Check `logs/weekly_report_*.log` for details

## 📝 Files to Edit

### Common Changes

**Change email recipient:**
```bash
# Edit .env
EMAIL_TO=new-recipient@gmail.com
```

**Change schedule:**
```bash
# Edit com.sscs.weeklyreport.plist
# Then reload scheduler
launchctl unload ~/Library/LaunchAgents/com.sscs.weeklyreport.plist
launchctl load ~/Library/LaunchAgents/com.sscs.weeklyreport.plist
```

**Add/remove fuel prefixes:**
```bash
# Edit config.yaml
fuel:
  diesel_prefixes: ['050', '019']
  regular_prefixes: ['001', '002', '003']
  def_prefixes: ['062']
```

## 🚀 Future Features

- ✅ Email automation with Gmail
- ✅ Weekly automatic scheduling
- ✅ Fuel breakdown by prefix
- ✅ Lottery breakdown by department
- ✅ Copy-paste section for Excel
- ⏳ Excel attachment generation (code ready, currently disabled)
- ⏳ Historical data backfill automation
- ⏳ Web dashboard for viewing reports

## 📚 Additional Documentation

- `HOW_IT_WORKS.md` - Detailed explanation of weekly check system

## 💡 Tips

- Run `python get_all_data.py` manually to see detailed terminal output
- Check `logs/wrapper.log` to see when the report last ran
- Use `test_email_only.py` to verify email works before full run
- Keep `HEADLESS=false` during initial testing to see browser actions
- The system is smart: won't run twice in the same week even if you trigger it manually

## 🆘 Support

For issues:
1. Check logs in `logs/` directory
2. Test email with `python test_email_only.py`
3. Verify credentials in `.env`
4. Check scheduler status: `launchctl list | grep sscs`

---

**Made with Claude Code** 🤖
