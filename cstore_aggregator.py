"""
C-Store data aggregator.
Collects Total C-Store Sales, Lottery, Scale, and calculates Other Sales.
"""


class CStoreAggregator:
    """Aggregates C-Store sales data from Store Stats"""

    def __init__(self, config, storestats_scraper, logger):
        """
        Initialize aggregator.

        Args:
            config (dict): Configuration dictionary
            storestats_scraper: StoreStatsScraper instance
            logger: Logger instance
        """
        self.config = config
        self.storestats = storestats_scraper
        self.logger = logger

    def collect_all_sales(self, start_date, end_date):
        """
        Collect all C-Store sales data for a date range.

        Args:
            start_date (str): Start date in YYYYMMDDhhmmss format
            end_date (str): End date in YYYYMMDDhhmmss format

        Returns:
            dict: {
                'total_cstore_sales': float,
                'lottery_sales': float,
                'scale_sales': float,
                'other_sales': float,
                'dept_27': float,
                'dept_43': float,
                'dept_72': float,
                'dept_88': float
            }
        """
        self.logger.info(f"Collecting C-Store data: {start_date} to {end_date}")

        # Get Total C-Store Sales
        total_cstore_sales = self.storestats.get_total_cstore_sales(start_date, end_date)

        # Get Lottery sales (Dept 27 + 43 + 72)
        self.logger.info("Collecting Lottery sales (Dept 27, 43, 72)...")
        dept_27 = self.storestats.get_department_sales(start_date, end_date, "27")
        dept_43 = self.storestats.get_department_sales(start_date, end_date, "43")
        dept_72 = self.storestats.get_department_sales(start_date, end_date, "72")
        lottery_sales = dept_27 + dept_43 + dept_72

        # Get Scale sales (Dept 88)
        self.logger.info("Collecting Scale sales (Dept 88)...")
        scale_sales = self.storestats.get_department_sales(start_date, end_date, "88")

        # Calculate Other Sales
        other_sales = total_cstore_sales - lottery_sales - scale_sales

        result = {
            'total_cstore_sales': total_cstore_sales,
            'lottery_sales': lottery_sales,
            'scale_sales': scale_sales,
            'other_sales': other_sales,
            'dept_27': dept_27,
            'dept_43': dept_43,
            'dept_72': dept_72,
            'dept_88': scale_sales  # dept_88 is the same as scale_sales
        }

        self.logger.info("C-Store data collected:")
        self.logger.info(f"  Total C-Store: ${result['total_cstore_sales']:,.2f}")
        self.logger.info(f"  Lottery: ${result['lottery_sales']:,.2f} (Dept 27: ${dept_27:,.2f}, Dept 43: ${dept_43:,.2f}, Dept 72: ${dept_72:,.2f})")
        self.logger.info(f"  Scale: ${result['scale_sales']:,.2f} (Dept 88)")
        self.logger.info(f"  Other: ${result['other_sales']:,.2f}")

        return result


if __name__ == '__main__':
    # Test the aggregator
    import os
    import sys
    import yaml
    import logging
    from dotenv import load_dotenv
    from sscs_scraper import SSCSScraper
    from storestats_scraper import StoreStatsScraper

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
    headless = os.getenv('HEADLESS', 'true').lower() == 'true'
    scraper.start_browser(headless=headless)
    scraper.login()

    # Test C-Store aggregator
    storestats = StoreStatsScraper(scraper, logger)
    aggregator = CStoreAggregator(config, storestats, logger)

    # Test dates (Oct 14-20, 2024)
    start_date = "20241014000000"
    end_date = "20241020235959"

    print("\n" + "=" * 70)
    print("C-STORE SALES DATA")
    print("=" * 70)

    cstore_data = aggregator.collect_all_sales(start_date, end_date)

    print(f"\nTotal C-Store: ${cstore_data['total_cstore_sales']:,.2f}")
    print(f"Lottery:       ${cstore_data['lottery_sales']:,.2f}")
    print(f"Scale:         ${cstore_data['scale_sales']:,.2f}")
    print(f"Other Sales:   ${cstore_data['other_sales']:,.2f}")
    print("=" * 70)

    scraper.close()
