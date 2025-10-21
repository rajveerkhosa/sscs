# SSCS Weekly Tracker Automation

Automated fuel gallons data extraction from SSCS Transaction Analysis and Excel tracker updates.

## Overview

This project automates the weekly process of:
- Logging into SSCS Transaction Analysis portal
- Extracting fuel gallons data (Diesel, Regular Gas, DEF) from Transaction Line Items
- Updating the Weekly Tracker Excel spreadsheet with scraped data
- Maintaining a rolling window of weekly data with automatic backups

## Features

- **Automated Data Extraction**: Scrapes fuel gallons from SSCS using Selenium WebDriver
- **Multiple Fuel Types**: Tracks Diesel (prefixes 050, 019), Regular Gas (001, 002, 003), and DEF (062)
- **Excel Integration**: Updates Weekly Tracker.xlsx with proper formatting preservation
- **Historical Backfill**: Can populate empty weeks with historical data from SSCS
- **Rolling Window**: Automatically hides oldest row when adding new week data
- **Automatic Backups**: Creates dated backups before any Excel modifications
- **Robust Error Handling**: Retry logic for slow-loading Angular tables
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## Requirements

### System Requirements
- Python 3.8+
- Firefox browser
- geckodriver (Firefox WebDriver)

### Python Dependencies
```
selenium
openpyxl
python-dotenv
pyyaml
```

## Installation

### 1. Install Firefox and geckodriver

**macOS:**
```bash
brew install firefox
brew install geckodriver
```

**Windows:**
- Download Firefox: https://www.mozilla.org/firefox/
- Download geckodriver: https://github.com/mozilla/geckodriver/releases
- Add geckodriver to PATH

### 2. Clone the Repository

```bash
git clone <repository-url>
cd SSCS
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.template .env
```

Edit `.env` and add your SSCS credentials:

```
SSCS_USER=your_username
SSCS_PASS=your_password
```

**Important:** Never commit the `.env` file to version control.

## Configuration

The `config.yaml` file contains all project settings:

- **SSCS Settings**: Login URL, base URL, site code
- **Week Settings**: Week ending day (Sunday), date format
- **Fuel Prefixes**: Product ID prefixes for each fuel type
- **Excel Settings**: Workbook path, sheet names, column mappings

Default configuration works out of the box for most setups.

## Usage

### Weekly Update (Current Week)

Run the main script every Monday morning to update the tracker with last week's data:

```bash
python main.py
```

This will:
1. Calculate the last full week (Monday-Sunday)
2. Log into SSCS
3. Scrape fuel gallons for all prefixes
4. Update the Excel tracker
5. Create a backup

**Run with visible browser (for debugging):**
```bash
HEADLESS=false python main.py
```

### Historical Backfill

To fill empty weeks with historical data:

```bash
python backfill_historical.py
```

The script will:
1. Scan the Excel file for empty weeks
2. Show you which weeks will be filled
3. Ask for confirmation
4. Scrape historical data from SSCS
5. Update the Excel file

### Testing

**Test environment setup:**
```bash
python check_env.py
```

**Test week calculations:**
```bash
python test_week_calc.py
```

## File Structure

```
SSCS/
├── main.py                    # Main weekly update script
├── backfill_historical.py     # Historical data backfill
├── restore_data_preserve_formatting.py  # Data restore utility
├── fix_formulas.py            # Formula fixing utility
├── sscs_scraper.py           # SSCS web scraping logic
├── fuel_aggregator.py        # Fuel data aggregation
├── excel_updater.py          # Excel file updates
├── week_utils.py             # Date/week calculations
├── config.yaml               # Configuration file
├── .env                      # Credentials (not in git)
├── .env.template             # Template for .env
├── requirements.txt          # Python dependencies
├── Weekly Tracker.xlsx       # Excel tracker (not in git)
├── backups/                  # Excel backups (not in git)
├── logs/                     # Log files (not in git)
└── exports/                  # Export folder (not in git)
```

## Excel File Structure

The automation expects `Weekly Tracker.xlsx` with:

- **Sheet**: "Weekly Gallons 25"
- **Column A**: Week ending labels (e.g., "Oct 20th")
- **Column B**: Diesel gallons
- **Column E**: Regular gas gallons
- **Column H**: DEF gallons
- **Column K**: Total gallons
- **Columns D, G, J, M**: Percentage formulas
- **Row with "Total"**: SUM formulas row

## Scheduling (Optional)

### macOS (cron)

Edit crontab:
```bash
crontab -e
```

Add this line to run every Monday at 7 AM:
```
0 7 * * 1 cd /Users/raj/SSCS && /usr/bin/python3 main.py
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Weekly, Monday, 7:00 AM
4. Action: Start a program
5. Program: `C:\Path\to\Python\python.exe`
6. Arguments: `main.py`
7. Start in: `C:\Path\to\SSCS`

## Troubleshooting

### Login Issues

**Error: "Login page did not load in time"**
- Check `.env` file format (no quotes, no spaces)
- Run `python check_env.py` to verify
- Try running with visible browser: `HEADLESS=false python main.py`

**Error: "Still on login page after submit"**
- Verify credentials are correct
- Check for SSCS error messages with visible browser

### Data Scraping Issues

**Error: "Qty column not found"**
- SSCS table structure may have changed
- Run with visible browser to inspect the table

**Diesel shows 0 gallons**
- Check if data exists for that week in SSCS
- Footer may be loading slowly - script retries 3 times

### Excel Update Issues

**Error: "Total row not found"**
- Verify Excel file has a row with "Total" in column A
- Check sheet name is exactly "Weekly Gallons 25"

**Excel file not updating**
- Close the Excel file before running the script
- VS Code or Excel may have the file locked

### General Issues

**Module not found errors**
```bash
pip install -r requirements.txt
```

**geckodriver not found**
```bash
# macOS
brew install geckodriver

# Verify installation
geckodriver --version
```

## Data Flow

1. **Week Calculation**: Determines last full week (Monday-Sunday)
2. **SSCS Login**: Authenticates with credentials from `.env`
3. **Data Extraction**: For each fuel prefix:
   - Navigates to Transaction Line Items page
   - Waits for Angular table to load
   - Finds Qty column in table header
   - Extracts total from footer row
4. **Aggregation**: Sums all prefixes by fuel type
5. **Excel Update**:
   - Creates dated backup
   - Finds or inserts row for the week
   - Writes fuel data to columns
   - Updates percentage formulas
   - Hides oldest visible row (rolling window)
   - Saves file

## Notes

- The script uses the **Sunday ending date** as the week label (e.g., "Oct 19th" for week Oct 13-19)
- Empty footer cells trigger automatic retry with 3-second waits
- All Excel formatting is preserved during updates
- Backups are created in `backups/` folder with format `Weekly Tracker_YYYY-MM-DD.xlsx`
- Logs are saved in `logs/` folder with timestamp
- Percentage formulas (D, G, J, M columns) are automatically applied to all data rows

## Security

- **Never commit** `.env` file (contains credentials)
- **Never commit** `Weekly Tracker.xlsx` (contains business data)
- **Never commit** `backups/` folder (contains sensitive data)
- Use `.gitignore` to exclude sensitive files
- Keep logs out of version control

## Utility Scripts

- **check_env.py**: Validates `.env` file format and credentials
- **test_week_calc.py**: Tests week calculation logic
- **backfill_historical.py**: Fills empty weeks with historical data
- **restore_data_preserve_formatting.py**: Restores data while preserving formatting
- **fix_formulas.py**: Fixes percentage and SUM formulas in Excel

## Support

For issues or questions:
1. Check the TROUBLESHOOTING.md file for detailed solutions
2. Review log files in `logs/` folder
3. Run diagnostic scripts: `check_env.py`, `test_week_calc.py`
4. Run with visible browser for debugging: `HEADLESS=false python main.py`
