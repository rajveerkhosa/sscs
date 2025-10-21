"""
SSCS web scraper for Transaction Line Items.
Handles login, navigation, and data extraction in scrape mode.
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SSCSScraper:
    """Scraper for SSCS Transaction Analysis App"""

    def __init__(self, config, logger=None):
        """
        Initialize the scraper.

        Args:
            config (dict): Configuration dictionary from config.yaml
            logger (logging.Logger, optional): Logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.driver = None

        # Get credentials from environment
        user_env = config['sscs']['credentials']['user_env']
        pass_env = config['sscs']['credentials']['pass_env']

        self.username = os.getenv(user_env)
        self.password = os.getenv(pass_env)

        if not self.username or not self.password:
            raise ValueError(f"Missing credentials: {user_env} or {pass_env} not set in .env")

    def start_browser(self, headless=True):
        """
        Start Firefox browser with options.

        Args:
            headless (bool): Run in headless mode
        """
        options = Options()
        if headless:
            options.add_argument('--headless')

        options.set_preference('browser.download.folderList', 2)
        options.set_preference('browser.download.manager.showWhenStarting', False)
        options.set_preference('browser.helperApps.neverAsk.saveToDisk',
                             'application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window()
        self.logger.info("Browser started")

    def login(self):
        """
        Log in to SSCS application.
        """
        login_url = self.config['sscs']['login_url']
        self.logger.info(f"Navigating to login: {login_url}")

        self.driver.get(login_url)

        try:
            # Wait for Angular app to initialize (longer timeout for Angular)
            self.logger.info("Waiting for login form to load (Angular app)...")

            # Wait for username field (using name attribute, not ID)
            username_field = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )

            # Additional wait for Angular to fully render
            time.sleep(2)

            # Find password field and login button
            password_field = self.driver.find_element(By.NAME, "password")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

            self.logger.info("Login form loaded, entering credentials...")

            # Enter credentials
            username_field.clear()
            username_field.send_keys(self.username)
            password_field.clear()
            password_field.send_keys(self.password)

            self.logger.info("Credentials entered, clicking login...")
            login_button.click()

            # Wait for login to complete and redirect
            # Look for successful navigation away from login page
            time.sleep(5)  # Give time for Angular to process login

            # Verify we're no longer on the login page
            current_url = self.driver.current_url
            if 'login' in current_url.lower():
                self.logger.warning(f"Still on login page after submit: {current_url}")
                self.logger.warning("Login may have failed - check credentials or page for errors")
            else:
                self.logger.info(f"Login successful, navigated to: {current_url}")

        except TimeoutException:
            self.logger.error("Login page did not load in time")
            self.logger.error("The login form (username field) was not found within 30 seconds")
            self.logger.error("This may indicate:")
            self.logger.error("  - Network issues")
            self.logger.error("  - SSCS site is down")
            self.logger.error("  - Login URL has changed")
            raise
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            raise

    def scrape_transaction_line_items(self, start_date, end_date, id_prefix):
        """
        Scrape Qty total from Transaction Line Items for a specific ID prefix.

        Args:
            start_date (str): Start date in YYYYMMDDhhmmss format
            end_date (str): End date in YYYYMMDDhhmmss format
            id_prefix (str): ID prefix to filter (e.g., '050')

        Returns:
            float: Total quantity (gallons) for this prefix
        """
        base_url = self.config['sscs']['base_url']
        site_code = self.config['sscs']['selected_site_code']
        department = self.config['fuel']['department']

        # Build URL with query parameters
        url = (
            f"{base_url}/#!/transactionlineitems/?"
            f"startDate={start_date}&"
            f"endDate={end_date}&"
            f"selectedSites={site_code}&"
            f"department={department}&"
            f"idstartswith={id_prefix}&"
            f"autosubmit=true"
        )

        self.logger.info(f"Navigating to Transaction Line Items for prefix {id_prefix}")
        self.logger.info(f"URL: {url}")
        self.driver.get(url)

        try:
            # Wait for Angular to initialize and load data
            self.logger.info("Waiting for table to load...")
            time.sleep(3)  # Give Angular time to start loading

            # Wait for table header to appear
            self.logger.info("Waiting for table header...")
            WebDriverWait(self.driver, 45).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table thead"))
            )

            # Wait for table body (data rows)
            self.logger.info("Waiting for table data...")
            WebDriverWait(self.driver, 45).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
            )

            # Extra wait for Angular to finish rendering
            time.sleep(5)
            self.logger.info("Table loaded, reading headers...")

            # Find Qty column index
            qty_col_index = self._find_qty_column_index()
            self.logger.info(f"Found Qty column at index {qty_col_index}")

            # Extract footer value
            qty_value = self._extract_footer_qty(qty_col_index)
            self.logger.info(f"Prefix {id_prefix}: {qty_value:,.2f} gallons")

            return qty_value

        except TimeoutException as e:
            self.logger.error(f"Table did not load for prefix {id_prefix}")
            self.logger.error(f"Timeout waiting for table elements")
            self._save_debug_screenshot(f"timeout_prefix_{id_prefix}")
            raise
        except Exception as e:
            self.logger.error(f"Error scraping prefix {id_prefix}: {e}")
            self._save_debug_screenshot(f"error_prefix_{id_prefix}")
            raise

    def _find_qty_column_index(self):
        """
        Find the index of the 'Qty' column in the table header.
        Uses JavaScript to read headers (handles scrollable tables).
        Tries multiple selector strategies for different table structures.

        Returns:
            int: 0-based index of Qty column
        """
        # Debug: Check table structure
        self.logger.info("=== Debugging table structure ===")

        try:
            table = self.driver.find_element(By.CSS_SELECTOR, "table")
            self.logger.info("✓ Table element found")

            # Check for thead
            try:
                thead = table.find_element(By.TAG_NAME, "thead")
                thead_rows = thead.find_elements(By.TAG_NAME, "tr")
                self.logger.info(f"✓ <thead> found with {len(thead_rows)} row(s)")
            except:
                self.logger.warning("✗ No <thead> element")
                thead = None

            # Check for tbody
            try:
                tbody = table.find_element(By.TAG_NAME, "tbody")
                tbody_rows = tbody.find_elements(By.TAG_NAME, "tr")
                self.logger.info(f"✓ <tbody> found with {len(tbody_rows)} row(s)")
            except:
                self.logger.warning("✗ No <tbody> element")

        except:
            self.logger.error("✗ No table element found!")

        # Strategy 1: Try thead tr:last-child th
        headers = None
        strategy_used = None

        try:
            self.logger.info("Strategy 1: Trying 'table thead tr:last-child th'...")
            header_row = self.driver.find_element(By.CSS_SELECTOR, "table thead tr:last-child")
            headers = header_row.find_elements(By.TAG_NAME, "th")
            if len(headers) > 0:
                strategy_used = "thead tr:last-child th"
                self.logger.info(f"✓ Found {len(headers)} <th> elements in thead")
        except:
            self.logger.info("✗ Strategy 1 failed")

        # Strategy 2: Try thead tr:last-child td (headers might be <td> not <th>)
        if not headers or len(headers) == 0:
            try:
                self.logger.info("Strategy 2: Trying 'table thead tr:last-child td'...")
                header_row = self.driver.find_element(By.CSS_SELECTOR, "table thead tr:last-child")
                headers = header_row.find_elements(By.TAG_NAME, "td")
                if len(headers) > 0:
                    strategy_used = "thead tr:last-child td"
                    self.logger.info(f"✓ Found {len(headers)} <td> elements in thead")
            except:
                self.logger.info("✗ Strategy 2 failed")

        # Strategy 3: Try any thead th
        if not headers or len(headers) == 0:
            try:
                self.logger.info("Strategy 3: Trying 'table thead th'...")
                headers = self.driver.find_elements(By.CSS_SELECTOR, "table thead th")
                if len(headers) > 0:
                    strategy_used = "thead th (any row)"
                    self.logger.info(f"✓ Found {len(headers)} <th> elements in thead")
            except:
                self.logger.info("✗ Strategy 3 failed")

        # Strategy 4: Try first row of table (might not have thead)
        if not headers or len(headers) == 0:
            try:
                self.logger.info("Strategy 4: Trying 'table tr:first-child th'...")
                header_row = self.driver.find_element(By.CSS_SELECTOR, "table tr:first-child")
                headers = header_row.find_elements(By.TAG_NAME, "th")
                if len(headers) > 0:
                    strategy_used = "tr:first-child th"
                    self.logger.info(f"✓ Found {len(headers)} <th> elements in first row")
            except:
                self.logger.info("✗ Strategy 4 failed")

        # Strategy 5: Try first row with td
        if not headers or len(headers) == 0:
            try:
                self.logger.info("Strategy 5: Trying 'table tr:first-child td'...")
                header_row = self.driver.find_element(By.CSS_SELECTOR, "table tr:first-child")
                headers = header_row.find_elements(By.TAG_NAME, "td")
                if len(headers) > 0:
                    strategy_used = "tr:first-child td"
                    self.logger.info(f"✓ Found {len(headers)} <td> elements in first row")
            except:
                self.logger.info("✗ Strategy 5 failed")

        if not headers or len(headers) == 0:
            self.logger.error("All strategies failed - could not find header elements")
            self._save_debug_screenshot("no_headers_found")
            raise ValueError("Could not find table headers with any selector strategy")

        self.logger.info(f"=== Using strategy: {strategy_used} ===")
        self.logger.info(f"Found {len(headers)} header elements")

        # Extract text from headers using JavaScript
        header_texts = []
        for idx, header in enumerate(headers):
            try:
                js_text = self.driver.execute_script("return arguments[0].innerText || arguments[0].textContent;", header)
                header_text = ' '.join(str(js_text).strip().split()) if js_text else ''
            except:
                header_text = ' '.join(header.text.strip().split())

            header_texts.append(f"[{idx}]: '{header_text}'")

        self.logger.info(f"Column headers: {', '.join(header_texts)}")

        # Try to find Qty column
        qty_variations = ['qty', 'qnty', 'quantity', 'gallon', 'gallons', 'volume']

        for idx, header in enumerate(headers):
            try:
                js_text = self.driver.execute_script("return arguments[0].innerText || arguments[0].textContent;", header)
                header_text = str(js_text).lower().strip() if js_text else ''
            except:
                header_text = header.text.lower().strip()

            for variation in qty_variations:
                if variation in header_text:
                    actual_text = self.driver.execute_script("return arguments[0].innerText || arguments[0].textContent;", header)
                    self.logger.info(f"✓ Matched column '{actual_text}' at index {idx} (contains '{variation}')")
                    return idx

        # No match found
        self.logger.error(f"Qty column not found. Searched for: {qty_variations}")
        self.logger.error(f"Available columns: {', '.join(header_texts)}")
        self._save_debug_screenshot("qty_column_not_matched")
        raise ValueError(f"Qty column not found in table headers. Columns found: {', '.join(header_texts)}")

    def _extract_footer_qty(self, qty_col_index):
        """
        Extract the Qty value from the table footer.
        Uses multiple strategies including pattern-based detection.

        Args:
            qty_col_index (int): Index of Qty column from header

        Returns:
            float: Parsed quantity value
        """
        try:
            self.logger.info(f"Looking for footer Qty value (header column index: {qty_col_index})")

            # Find footer row
            try:
                footer_row = self.driver.find_element(By.CSS_SELECTOR, "table tfoot tr")
                self.logger.info("✓ Using tfoot for footer")
            except NoSuchElementException:
                self.logger.info("No tfoot found, searching for summary row...")
                footer_candidates = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

                footer_row = None
                for row in reversed(footer_candidates):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    footer_cells = [c for c in cells if 'footer' in c.get_attribute('class')]
                    if len(footer_cells) > 0:
                        footer_row = row
                        self.logger.info(f"✓ Using summary row with {len(footer_cells)} footer cells")
                        break

                if footer_row is None:
                    self.logger.error("Footer row not found")
                    raise ValueError("Footer row not found")

            # Get all footer cells
            cells = footer_row.find_elements(By.TAG_NAME, "td")
            self.logger.info(f"Footer row has {len(cells)} <td> elements")

            # Extract text from all cells using JavaScript (for debugging)
            all_cell_texts = []
            actual_cell_values = []
            for idx, cell in enumerate(cells):
                try:
                    cell_text = self.driver.execute_script("return arguments[0].innerText || arguments[0].textContent;", cell)
                    cell_text = str(cell_text).strip() if cell_text else ''
                except:
                    cell_text = cell.text.strip()

                actual_cell_values.append(cell_text)
                all_cell_texts.append(f"[{idx}]: '{cell_text}'")

            self.logger.info(f"Footer cells: {', '.join(all_cell_texts)}")

            # Check if all footer cells are empty (may need to wait longer for Angular)
            if all(val == '' for val in actual_cell_values):
                self.logger.info("Footer appears empty - retrying with longer wait...")

                # Retry up to 3 times with increasing waits
                for retry in range(1, 4):
                    self.logger.info(f"Retry {retry}/3: Waiting 3 seconds for footer to load...")
                    time.sleep(3)

                    # Re-find footer row and cells (avoid stale elements)
                    try:
                        footer_row_fresh = self.driver.find_element(By.CSS_SELECTOR, "table tfoot tr")
                    except NoSuchElementException:
                        # Try summary row again
                        footer_candidates = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                        footer_row_fresh = None
                        for row in reversed(footer_candidates):
                            row_cells = row.find_elements(By.TAG_NAME, "td")
                            footer_cells = [c for c in row_cells if 'footer' in c.get_attribute('class')]
                            if len(footer_cells) > 0:
                                footer_row_fresh = row
                                break
                        if footer_row_fresh is None:
                            self.logger.warning(f"Retry {retry}: Footer row not found")
                            continue

                    # Get fresh cell elements and update the original cells variable
                    cells = footer_row_fresh.find_elements(By.TAG_NAME, "td")

                    # Re-read all footer cells from fresh elements
                    actual_cell_values = []
                    all_cell_texts = []
                    for idx, cell in enumerate(cells):
                        try:
                            cell_text = self.driver.execute_script("return arguments[0].innerText || arguments[0].textContent;", cell)
                            cell_text = str(cell_text).strip() if cell_text else ''
                        except:
                            try:
                                cell_text = cell.text.strip()
                            except:
                                cell_text = ''

                        actual_cell_values.append(cell_text)
                        all_cell_texts.append(f"[{idx}]: '{cell_text}'")

                    self.logger.info(f"Retry {retry} footer cells: {', '.join(all_cell_texts)}")

                    # Check if we now have data
                    if not all(val == '' for val in actual_cell_values):
                        self.logger.info(f"✓ Footer loaded on retry {retry}")
                        break
                else:
                    # All retries failed - truly no data
                    self.logger.info("Footer still empty after 3 retries - returning 0.00 gallons")
                    return 0.0

            # Strategy 1: Try using column index from header
            qty_value = None
            if qty_col_index < len(cells):
                qty_cell = cells[qty_col_index]
                try:
                    qty_text = self.driver.execute_script("return arguments[0].innerText || arguments[0].textContent;", qty_cell)
                    qty_text = str(qty_text).strip() if qty_text else ''
                except:
                    qty_text = qty_cell.text.strip()

                self.logger.info(f"Strategy 1 (index match): Cell[{qty_col_index}] = '{qty_text}'")

                if qty_text and self._is_qty_value(qty_text):
                    qty_value = self._parse_qty_value(qty_text)
                    self.logger.info(f"✓ Strategy 1 succeeded: {qty_value:,.2f}")
                else:
                    self.logger.warning(f"Strategy 1 failed: Cell empty or doesn't look like Qty")

            # Strategy 2: Search all footer cells for Qty pattern
            if qty_value is None:
                self.logger.info("Strategy 2: Searching all footer cells for Qty pattern...")

                for idx, cell in enumerate(cells):
                    try:
                        cell_text = self.driver.execute_script("return arguments[0].innerText || arguments[0].textContent;", cell)
                        cell_text = str(cell_text).strip() if cell_text else ''
                    except:
                        cell_text = cell.text.strip()

                    if cell_text and self._is_qty_value(cell_text):
                        qty_value = self._parse_qty_value(cell_text)
                        self.logger.info(f"✓ Strategy 2 succeeded: Found Qty at cell[{idx}] = {qty_value:,.2f}")
                        break

            if qty_value is None:
                self.logger.error("Both strategies failed - could not find Qty value in footer")
                self.logger.error(f"Footer cells were: {', '.join(all_cell_texts)}")
                self._save_debug_screenshot("footer_qty_not_found")
                raise ValueError("Could not extract Qty value from footer")

            self.logger.info(f"Final Qty value: {qty_value:,.2f}")
            return qty_value

        except Exception as e:
            self.logger.error(f"Error extracting footer Qty: {e}")
            self._save_debug_screenshot("footer_extraction_error")
            raise

    def _is_qty_value(self, text):
        """
        Check if a text value looks like a Qty (gallons) value.
        Qty values are numeric, may have commas, have decimal point, NO dollar sign.

        Args:
            text (str): Text to check

        Returns:
            bool: True if this looks like a Qty value
        """
        if not text:
            return False

        # Remove whitespace
        text = text.strip()

        # Reject if it has a dollar sign (that's a money amount)
        if '$' in text:
            return False

        # Reject if it's just dashes or empty
        if text in ['-', '--', '---', '']:
            return False

        # Must contain at least one digit
        if not any(c.isdigit() for c in text):
            return False

        # Try to parse it as a number
        try:
            clean_text = text.replace(',', '')
            value = float(clean_text)
            # Qty values should be positive and reasonable (0-1000000 gallons)
            if value >= 0 and value < 1000000:
                return True
        except:
            return False

        return False

    def _parse_qty_value(self, text):
        """
        Parse a Qty value from text.

        Args:
            text (str): Text containing quantity (e.g., "1,565.80")

        Returns:
            float: Parsed value
        """
        clean_text = text.strip().replace(',', '')
        return float(clean_text)

    def sanity_check_pagination(self, start_date, end_date, id_prefix):
        """
        Optional sanity check: change records per page and verify footer doesn't change.

        Args:
            start_date (str): Start date
            end_date (str): End date
            id_prefix (str): ID prefix to test

        Returns:
            bool: True if sanity check passed
        """
        self.logger.info(f"Running pagination sanity check for prefix {id_prefix}")

        try:
            # Get initial value
            initial_qty = self.scrape_transaction_line_items(start_date, end_date, id_prefix)

            # Change records per page (if dropdown exists)
            try:
                # Look for records per page selector
                page_size_select = self.driver.find_element(By.CSS_SELECTOR, "select[ng-model*='pageSize'], select[ng-model*='recordsPerPage']")

                # Change to different value
                from selenium.webdriver.support.ui import Select
                select = Select(page_size_select)
                original_value = select.first_selected_option.get_attribute('value')

                # Pick a different value
                options = [opt.get_attribute('value') for opt in select.options]
                new_value = options[1] if options[0] == original_value else options[0]

                select.select_by_value(new_value)
                time.sleep(2)

                # Re-check footer
                qty_col_index = self._find_qty_column_index()
                new_qty = self._extract_footer_qty(qty_col_index)

                if abs(initial_qty - new_qty) > 0.01:
                    self.logger.warning(
                        f"SANITY CHECK FAILED: Qty changed from {initial_qty} to {new_qty} when changing page size!"
                    )
                    return False
                else:
                    self.logger.info("Pagination sanity check passed")
                    return True

            except NoSuchElementException:
                self.logger.info("Page size selector not found, skipping pagination check")
                return True

        except Exception as e:
            self.logger.warning(f"Sanity check error (non-critical): {e}")
            return True

    def _save_debug_screenshot(self, filename_prefix):
        """
        Save a screenshot for debugging purposes.

        Args:
            filename_prefix (str): Prefix for the screenshot filename
        """
        try:
            if self.driver:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                screenshot_path = f"logs/{filename_prefix}_{timestamp}.png"
                self.driver.save_screenshot(screenshot_path)
                self.logger.info(f"Debug screenshot saved: {screenshot_path}")
        except Exception as e:
            self.logger.warning(f"Could not save screenshot: {e}")

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed")


if __name__ == '__main__':
    # Test scraper
    import yaml
    from dotenv import load_dotenv
    from week_utils import get_week_params

    logging.basicConfig(level=logging.INFO)

    load_dotenv()

    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    week_params = get_week_params()

    scraper = SSCSScraper(config)
    try:
        scraper.start_browser(headless=False)
        scraper.login()

        # Test one prefix
        qty = scraper.scrape_transaction_line_items(
            week_params['start_date'],
            week_params['end_date'],
            '050'
        )
        print(f"Test result: {qty} gallons")

    finally:
        scraper.close()
