"""
Store Stats scraper for SSCS Transaction Analysis.
Scrapes Total C-Store Sales and department-specific data.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class StoreStatsScraper:
    """Scrapes Store Stats data from SSCS Transaction Analysis"""

    def __init__(self, scraper, logger):
        """
        Initialize StoreStats scraper.

        Args:
            scraper: SSCSScraper instance (already logged in)
            logger: Logger instance
        """
        self.scraper = scraper
        self.driver = scraper.driver
        self.logger = logger
        self.config = scraper.config

    def navigate_to_storestats(self, start_date, end_date):
        """
        Navigate to Store Stats page with date range.

        Args:
            start_date (str): Start date in YYYYMMDDhhmmss format
            end_date (str): End date in YYYYMMDDhhmmss format
        """
        selected_site = self.config['sscs']['selected_site_code']
        url = (
            f"{self.config['sscs']['base_url']}/#!/storestats/"
            f"?startDate={start_date}"
            f"&endDate={end_date}"
            f"&selectedSites={selected_site}"
            f"&reportClass=single"
            f"&autosubmit=true"
        )

        self.logger.info(f"Navigating to Store Stats: {start_date} to {end_date}")
        self.driver.get(url)

        # Wait for page to load
        time.sleep(5)

    def get_total_cstore_sales(self, start_date, end_date):
        """
        Get Total Merchandise Sales from Store Stats.
        This is the dollar amount from the "Total Merchandise Sales" column.

        Args:
            start_date (str): Start date in YYYYMMDDhhmmss format
            end_date (str): End date in YYYYMMDDhhmmss format

        Returns:
            float: Total Merchandise Sales
        """
        self.navigate_to_storestats(start_date, end_date)

        # Wait for table to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
            )
        except TimeoutException:
            self.logger.warning("Table did not load in time")
            return 0.0

        # Extra wait for Angular to render
        time.sleep(5)

        # Find the data row (there's usually only 1 row for single site)
        try:
            # Get all rows from tbody - use ng-scope class to get actual data rows (not headers)
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr.ng-scope")

            if not rows:
                self.logger.warning("No data rows found with .ng-scope class, trying all tbody rows")
                # Fallback: get all rows and filter
                rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

            if not rows:
                self.logger.warning("No rows found in table")
                return 0.0

            self.logger.info(f"Found {len(rows)} row(s) in Store Stats table")

            # Get the last row (should be the data row with site totals)
            data_row = rows[-1]

            # Get all td cells in the row
            cells = data_row.find_elements(By.TAG_NAME, "td")

            # Read text using multiple methods to ensure we get the actual content
            cell_texts = []
            for i, cell in enumerate(cells):
                try:
                    # Try innerText first (better for rendered text)
                    text = self.driver.execute_script("return arguments[0].innerText;", cell)
                    if not text or text.strip() == '':
                        # Fallback to textContent
                        text = self.driver.execute_script("return arguments[0].textContent;", cell)
                    if not text or text.strip() == '':
                        # Last resort: use .text property
                        text = cell.text
                    cell_texts.append(text.strip())
                except Exception as e:
                    self.logger.debug(f"Error reading cell {i}: {e}")
                    cell_texts.append("")

            self.logger.info(f"Store Stats row cells ({len(cell_texts)} cells): {cell_texts}")

            # Column structure (based on screenshot):
            # 0: Site, 1: Number Transactions, 2: Number Merchandise Transactions,
            # 3: Total Merchandise Sales, 4: Avg Merchandise Sales, 5: Take Rate, ...

            # The "Total Merchandise Sales" is typically column 3 (4th column, 0-indexed)
            # But let's also search for the largest $ value as backup

            # Try column 3 first
            if len(cell_texts) > 3 and '$' in cell_texts[3]:
                value_str = cell_texts[3].replace('$', '').replace(',', '').strip()
                try:
                    total_sales = float(value_str)
                    self.logger.info(f"Total C-Store Sales (from column 3): ${total_sales:,.2f}")
                    return total_sales
                except ValueError:
                    pass

            # Fallback: Find largest $ value
            max_sales = 0.0
            for i, text in enumerate(cell_texts):
                if '$' in text:
                    value_str = text.replace('$', '').replace(',', '').strip()
                    try:
                        sales_value = float(value_str)
                        if sales_value > max_sales:
                            max_sales = sales_value
                            self.logger.debug(f"Found ${sales_value:,.2f} in column {i}")
                    except ValueError:
                        continue

            if max_sales > 1000:  # Sanity check - should be substantial
                self.logger.info(f"Total C-Store Sales (largest value): ${max_sales:,.2f}")
                return max_sales
            else:
                self.logger.warning(f"Total C-Store Sales value too small or not found: ${max_sales:,.2f}")
                return 0.0

        except Exception as e:
            self.logger.error(f"Error getting Total C-Store Sales: {e}")
            import traceback
            traceback.print_exc()
            return 0.0

    def get_department_sales(self, start_date, end_date, department, max_retries=3):
        """
        Get sales for a specific department from Transaction Line Items page.
        Gets the "Sale Amount" from the footer.

        Args:
            start_date (str): Start date in YYYYMMDDhhmmss format
            end_date (str): End date in YYYYMMDDhhmmss format
            department (str): Department number (e.g., "27", "43", "72", "88")
            max_retries (int): Maximum number of retries for page load/parsing

        Returns:
            float: Department sales (Sale Amount)
        """
        from selenium.common.exceptions import StaleElementReferenceException

        for attempt in range(max_retries):
            try:
                # Navigate to Transaction Line Items page for this department
                selected_site = self.config['sscs']['selected_site_code']
                url = (
                    f"{self.config['sscs']['base_url']}/#!/transactionlineitems/"
                    f"?startDate={start_date}"
                    f"&endDate={end_date}"
                    f"&selectedSites={selected_site}"
                    f"&department={department}"
                    f"&autosubmit=true"
                )

                if attempt > 0:
                    self.logger.info(f"Retry {attempt}/{max_retries-1} for Dept {department}")
                else:
                    self.logger.info(f"Navigating to Transaction Line Items for Dept {department}")

                self.driver.get(url)

                # Wait for table to load with longer timeout for slow connections
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
                    )
                except TimeoutException:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Table load timeout for dept {department}, retrying...")
                        time.sleep(3)
                        continue
                    else:
                        self.logger.warning(f"Table did not load for dept {department} after {max_retries} attempts")
                        return 0.0

                # Extra wait for Angular to fully render
                time.sleep(8)

                # Find the footer row and get Sale Amount column
                # Try to find footer row
                footer_row = None
                try:
                    footer_row = self.driver.find_element(By.CSS_SELECTOR, "table tfoot tr")
                except NoSuchElementException:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"No footer found for dept {department}, retrying...")
                        time.sleep(2)
                        continue
                    else:
                        self.logger.warning(f"Could not find footer for dept {department} after {max_retries} attempts")
                        return 0.0

                # Get all td cells in footer - use JavaScript to avoid stale element issues
                cell_texts = []
                try:
                    # Get cell count first
                    cell_count = self.driver.execute_script(
                        "return arguments[0].querySelectorAll('td').length;",
                        footer_row
                    )

                    # Read each cell using JavaScript directly
                    for i in range(cell_count):
                        text = self.driver.execute_script(
                            "return arguments[0].querySelectorAll('td')[arguments[1]].textContent;",
                            footer_row, i
                        )
                        cell_texts.append(text.strip() if text else "")

                except StaleElementReferenceException:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Stale element for dept {department}, retrying...")
                        time.sleep(2)
                        continue
                    else:
                        raise

                self.logger.debug(f"Dept {department} footer cells: {cell_texts}")

                # The "Sale Amount" column should have a $ value
                # Find the last column with a dollar sign (usually the Sale Amount)
                sale_amount = 0.0
                for text in reversed(cell_texts):  # Start from the end
                    if '$' in text:
                        # Parse the value
                        value_str = text.replace('$', '').replace(',', '').strip()
                        try:
                            sale_amount = float(value_str)
                            self.logger.info(f"Dept {department} Sale Amount: ${sale_amount:,.2f}")
                            return sale_amount
                        except ValueError:
                            continue

                # If we got here but found no $ value, check if page loaded correctly
                if not cell_texts or all(not c for c in cell_texts):
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Empty footer cells for dept {department}, retrying...")
                        time.sleep(2)
                        continue
                    else:
                        self.logger.warning(f"Could not parse Sale Amount for dept {department} - no data in footer")
                        return 0.0

                self.logger.warning(f"Could not parse Sale Amount for dept {department}")
                return 0.0

            except StaleElementReferenceException as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Stale element error for dept {department}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    self.logger.error(f"Stale element error for dept {department} after {max_retries} attempts: {e}")
                    return 0.0
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Error getting dept {department} sales (attempt {attempt+1}): {e}")
                    time.sleep(2)
                    continue
                else:
                    self.logger.error(f"Error getting dept {department} sales after {max_retries} attempts: {e}")
                    import traceback
                    traceback.print_exc()
                    return 0.0

        return 0.0


if __name__ == '__main__':
    # Test the scraper
    import os
    import sys
    import yaml
    import logging
    from dotenv import load_dotenv
    from sscs_scraper import SSCSScraper

    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    logger = logging.getLogger(__name__)

    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Initialize and login
    scraper = SSCSScraper(config, logger)
    # Force headless=False to see the browser
    scraper.start_browser(headless=False)
    scraper.login()

    # Test Store Stats
    storestats = StoreStatsScraper(scraper, logger)

    # Test dates (Oct 14-20, 2024)
    start_date = "20241014000000"
    end_date = "20241020235959"

    print("\nTesting Store Stats scraper:")
    print("=" * 50)

    total_sales = storestats.get_total_cstore_sales(start_date, end_date)
    print(f"Total C-Store Sales: ${total_sales:,.2f}")

    dept_27 = storestats.get_department_sales(start_date, end_date, "27")
    dept_43 = storestats.get_department_sales(start_date, end_date, "43")
    dept_72 = storestats.get_department_sales(start_date, end_date, "72")
    lottery_total = dept_27 + dept_43 + dept_72
    print(f"\nLottery (27+43+72): ${lottery_total:,.2f}")

    dept_88 = storestats.get_department_sales(start_date, end_date, "88")
    print(f"Scale (88): ${dept_88:,.2f}")

    other_sales = total_sales - lottery_total - dept_88
    print(f"Other Sales: ${other_sales:,.2f}")

    scraper.close()
