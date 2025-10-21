# SSCS Weekly Tracker - Project Summary

## Overview

Automated weekly fuel data scraper and Excel updater for SSCS Transaction Analysis system.

**Mode:** Scrape-only (no file downloads)
**Schedule:** Weekly, every Monday at 7:00 AM
**Target:** Weekly Tracker.xlsx

## Project Structure

```
SSCS/
├── Core Scripts
│   ├── main.py                 # Main orchestration script
│   ├── week_utils.py           # Week calculation (last Sunday, ordinal dates)
│   ├── sscs_scraper.py         # Selenium web scraper for SSCS
│   ├── fuel_aggregator.py      # Fuel data aggregation logic
│   └── excel_updater.py        # Excel update with formatting preservation
│
├── Configuration
│   ├── config.yaml             # Site codes, prefixes, column mappings
│   ├── .env.template           # Template for credentials
│   └── .env                    # Your credentials (NOT tracked)
│
├── Documentation
│   ├── QUICKSTART.md           # 5-minute setup guide
│   ├── README.md               # Full documentation
│   ├── SCHEDULER_SETUP.md      # Windows Task Scheduler guide
│   └── PROJECT_SUMMARY.md      # This file
│
├── Testing & Utilities
│   ├── test_week_calc.py       # Configuration validation script
│   ├── run_sscs_update.bat     # Windows quick-run
│   └── run_sscs_update.sh      # macOS/Linux quick-run
│
├── Data
│   ├── Weekly Tracker.xlsx     # YOUR tracker file (place here)
│   ├── backups/                # Dated backups (auto-created)
│   ├── logs/                   # Run logs (auto-created)
│   └── exports/                # (unused in scrape mode)
│
└── Dependencies
    ├── requirements.txt        # Python packages
    └── .gitignore             # Git exclusions
```

## Architecture

### 1. Week Calculation (`week_utils.py`)
- Finds last full Sunday (strictly before today)
- Calculates Mon 00:00:00 to Sun 23:59:59
- Formats as YYYYMMDDhhmmss for SSCS
- Generates ordinal labels (e.g., "22nd Sep")

### 2. SSCS Scraper (`sscs_scraper.py`)
- Selenium-based Firefox automation
- Logs into SSCS with .env credentials
- Navigates to Transaction Line Items with query params
- Maps "Qty" header to column index
- Extracts footer totals (handles tfoot or summary row)
- Supports optional pagination sanity check

### 3. Fuel Aggregator (`fuel_aggregator.py`)
- Collects data for each ID prefix:
  - **Diesel:** 050, 019
  - **Regular:** 001, 002, 003
  - **DEF:** 062
- Aggregates by fuel type
- Validates: diesel + regular + DEF = total
- Logs per-prefix breakdown

### 4. Excel Updater (`excel_updater.py`)
- Creates dated backup before update
- Finds "Total" row in each sheet
- Checks if week already exists (updates in place)
- Otherwise:
  - Inserts row above "Total"
  - Copies formatting from previous row
  - Writes data to mapped columns
  - Hides oldest visible row (rolling window)
- Preserves formulas, borders, number formats, conditional formatting

### 5. Main Orchestration (`main.py`)
- Loads config and environment
- Sets up dual logging (file + console)
- Runs week calculation
- Initializes scraper and logs in
- Collects fuel data
- Updates Excel with backups
- Comprehensive error handling

## Data Flow

```
1. Calculate Week
   └→ Mon 00:00:00 to Sun 23:59:59
      └→ SSCS format: YYYYMMDDhhmmss
         └→ Excel label: "22nd Sep"

2. Login to SSCS
   └→ Navigate to base_url
      └→ For each prefix (050, 019, 001, 002, 003, 062):
         └→ Build URL with params
            └→ Wait for table
               └→ Find Qty column
                  └→ Extract footer value

3. Aggregate Data
   └→ diesel_gal = 050 + 019
   └→ regular_gal = 001 + 002 + 003
   └→ def_gal = 062
   └→ total_gal = diesel + regular + DEF
   └→ Sanity check: sum(all prefixes) == total

4. Update Excel
   └→ Backup to backups/
      └→ For each enabled sheet:
         └→ Find Total row
            └→ Insert/update week row
               └→ Write fuel data to columns
                  └→ Hide oldest row
                     └→ Save workbook
```

## Configuration Points

### SSCS Settings (`config.yaml`)
```yaml
sscs:
  login_url: "..."
  base_url: "..."
  selected_site_code: "006579001"
```

### Fuel Prefixes (`config.yaml`)
```yaml
fuel:
  department: "1"
  diesel_prefixes: ["050", "019"]
  regular_prefixes: ["001", "002", "003"]
  def_prefixes: ["062"]
```

### Excel Columns (`config.yaml`)
```yaml
sheets:
  - name: "Gallons v Last Year"
    thisweek_columns:
      diesel_gal: "B"    # Diesel (This week)
      regular_gal: "E"   # Gas (This week)
      def_gal: "H"       # DEF (This week)
      total_gal: "K"     # Total (This week)
```

### Credentials (`.env`)
```
SSCS_USER=your_username
SSCS_PASS=your_password
```

### Optional Env Vars
```
HEADLESS=false         # Show browser (default: true)
RUN_SANITY_CHECK=true  # Run pagination check (default: false)
```

## Key Features

### ✓ Scrape Mode
- No file downloads
- Direct table reading
- Header-to-column mapping
- Footer total extraction

### ✓ Rolling Window
- Insert new row above "Total"
- Hide oldest row (not deleted)
- Maintains constant visible height
- Preserves all data for formulas

### ✓ Format Preservation
- Copies cell styles from previous row
- Maintains borders, fills, fonts
- Preserves number formats
- Keeps conditional formatting scopes

### ✓ Safety
- Creates dated backups before update
- Validates Total row exists
- Checks week label doesn't duplicate (unless updating)
- Sanity checks: total == sum(parts)

### ✓ Logging
- Timestamped log files
- Dual output (file + console)
- Per-prefix breakdown
- Success/failure tracking

## Usage Patterns

### Manual Run
```bash
python main.py
```

### Test Configuration
```bash
python test_week_calc.py
```

### With Visible Browser
```bash
HEADLESS=false python main.py
```

### Windows Double-Click
```cmd
run_sscs_update.bat
```

### Scheduled (Windows)
```
Task Scheduler → Weekly Monday 7 AM
Program: python
Arguments: main.py
Start in: C:\Path\To\SSCS
```

### Scheduled (macOS/Linux)
```bash
# crontab -e
0 7 * * 1 cd /path/to/SSCS && python3 main.py
```

## Dependencies

```
selenium>=4.15.0       # Web automation
openpyxl>=3.1.2        # Excel read/write
python-dotenv>=1.0.0   # .env loading
PyYAML>=6.0.1          # YAML config
```

**External:**
- Firefox browser
- geckodriver (Firefox WebDriver)

## Acceptance Tests

| Test | Expected Result |
|------|-----------------|
| Week calculation | Last full Sunday (Mon-Sun) |
| Ordinal labels | "1st", "2nd", "3rd", "21st", "22nd" |
| Diesel total | Sum of prefixes 050 + 019 |
| Regular total | Sum of 001 + 002 + 003 |
| DEF total | Sum of 062 |
| Grand total | diesel + regular + DEF |
| Excel row | New row above "Total" |
| Week label | Matches calculated week |
| Oldest row | Hidden (not deleted) |
| Formatting | Matches previous row |
| Backup | Dated file in backups/ |
| Log | Detailed log in logs/ |

## Troubleshooting

### Script Level
- Check `logs/` for detailed error messages
- Run with `HEADLESS=false` to see browser
- Verify .env has correct credentials
- Run `test_week_calc.py` to validate config

### SSCS Level
- Table structure changed → Check header mapping
- Login failed → Verify credentials
- Qty value wrong → Check ID prefix filters
- Department filter → Ensure dept=1

### Excel Level
- "Total" row not found → Check column A
- Formatting broken → Restore from backup
- Wrong columns → Check config.yaml mappings
- Sheet not found → Verify sheet names match

## Maintenance

### Weekly Monitoring (First Month)
1. Check log files after each run
2. Verify Excel data accuracy
3. Confirm gallons match SSCS manually
4. Ensure backups are created

### Monthly Review
1. Review log files for warnings
2. Check backup folder size
3. Verify hidden rows accumulation
4. Test manual run occasionally

### Updates
- **Config changes:** Edit `config.yaml`
- **Credential updates:** Edit `.env`
- **Column remapping:** Update `config.yaml` sheets section
- **New fuel types:** Add to `fuel` section

## File Sizes

| File | Size |
|------|------|
| main.py | ~6 KB |
| sscs_scraper.py | ~11 KB |
| excel_updater.py | ~11 KB |
| fuel_aggregator.py | ~5 KB |
| week_utils.py | ~3 KB |
| **Total code** | **~36 KB** |

## Performance

- **Week calculation:** <1 second
- **Login:** ~3-5 seconds
- **Per-prefix scrape:** ~5-10 seconds
- **6 prefixes:** ~30-60 seconds
- **Excel update:** ~2-3 seconds
- **Total runtime:** ~1-2 minutes

## Security Notes

- `.env` is gitignored (never commit credentials)
- `.env.template` provides structure without secrets
- Logs do NOT contain passwords
- Browser can run headless (no GUI)
- Credentials loaded only at runtime

## Future Enhancements (Optional)

### Phase 2: C-Store Sales
- Enable Store Stats scraping
- Add `cstore_sales` to Excel
- Update "C Store Sales v Last Year" sheet

### Phase 3: Additional Metrics
- Lottery sales (if available)
- Scale data
- Custom date ranges

### Phase 4: Notifications
- Email on completion
- Slack/Discord webhooks
- Error alerts

## Support

**Before reporting issues:**
1. Run `python test_week_calc.py`
2. Check latest log file
3. Try with `HEADLESS=false`
4. Verify Excel and .env files exist
5. Review README.md and SCHEDULER_SETUP.md

**Log locations:**
- Run logs: `logs/sscs_update_YYYY-MM-DD_HH-MM-SS.log`
- Backups: `backups/Weekly Tracker_YYYY-MM-DD.xlsx`

## License

MIT

---

**Created:** October 2025
**Last Updated:** October 2025
**Version:** 1.0
**Status:** Production Ready
