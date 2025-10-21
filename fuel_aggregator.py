"""
Fuel data aggregation logic.
Collects gallons from all prefixes and aggregates into diesel, regular, DEF, and total.
"""

import logging


class FuelAggregator:
    """Aggregates fuel data from multiple ID prefixes"""

    def __init__(self, config, scraper, logger=None):
        """
        Initialize aggregator.

        Args:
            config (dict): Configuration dictionary
            scraper (SSCSScraper): Instance of SSCS scraper
            logger (logging.Logger, optional): Logger instance
        """
        self.config = config
        self.scraper = scraper
        self.logger = logger or logging.getLogger(__name__)

        # Get prefix lists from config
        self.diesel_prefixes = config['fuel']['diesel_prefixes']
        self.regular_prefixes = config['fuel']['regular_prefixes']
        self.def_prefixes = config['fuel']['def_prefixes']

    def collect_all_gallons(self, start_date, end_date):
        """
        Collect gallons for all prefixes and aggregate.

        Args:
            start_date (str): Start date in YYYYMMDDhhmmss format
            end_date (str): End date in YYYYMMDDhhmmss format

        Returns:
            dict: {
                'diesel_gal': float,
                'regular_gal': float,
                'def_gal': float,
                'total_gal': float,
                'prefix_details': {prefix: gallons, ...}
            }
        """
        self.logger.info("Starting fuel data collection...")

        prefix_details = {}

        # Collect diesel
        diesel_gal = 0.0
        for prefix in self.diesel_prefixes:
            qty = self.scraper.scrape_transaction_line_items(start_date, end_date, prefix)
            prefix_details[prefix] = qty
            diesel_gal += qty

        self.logger.info(f"Diesel total: {diesel_gal:,.2f} gallons (prefixes: {self.diesel_prefixes})")

        # Collect regular (gas)
        regular_gal = 0.0
        for prefix in self.regular_prefixes:
            qty = self.scraper.scrape_transaction_line_items(start_date, end_date, prefix)
            prefix_details[prefix] = qty
            regular_gal += qty

        self.logger.info(f"Regular gas total: {regular_gal:,.2f} gallons (prefixes: {self.regular_prefixes})")

        # Collect DEF
        def_gal = 0.0
        for prefix in self.def_prefixes:
            qty = self.scraper.scrape_transaction_line_items(start_date, end_date, prefix)
            prefix_details[prefix] = qty
            def_gal += qty

        self.logger.info(f"DEF total: {def_gal:,.2f} gallons (prefixes: {self.def_prefixes})")

        # Calculate total
        total_gal = diesel_gal + regular_gal + def_gal

        self.logger.info(f"TOTAL: {total_gal:,.2f} gallons")

        # Sanity check
        calculated_total = sum(prefix_details.values())
        if abs(calculated_total - total_gal) > 0.01:
            self.logger.warning(
                f"SANITY CHECK FAILED: Sum of all prefixes ({calculated_total:,.2f}) "
                f"!= diesel + regular + DEF ({total_gal:,.2f})"
            )
        else:
            self.logger.info("Sanity check passed: totals match")

        return {
            'diesel_gal': diesel_gal,
            'regular_gal': regular_gal,
            'def_gal': def_gal,
            'total_gal': total_gal,
            'prefix_details': prefix_details
        }

    def run_sanity_check(self, start_date, end_date):
        """
        Run optional pagination sanity check on one prefix.

        Args:
            start_date (str): Start date
            end_date (str): End date

        Returns:
            bool: True if passed
        """
        # Pick first diesel prefix for sanity check
        test_prefix = self.diesel_prefixes[0]
        return self.scraper.sanity_check_pagination(start_date, end_date, test_prefix)


if __name__ == '__main__':
    # Test aggregator
    import yaml
    from dotenv import load_dotenv
    from week_utils import get_week_params
    from sscs_scraper import SSCSScraper

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    load_dotenv()

    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    week_params = get_week_params()

    scraper = SSCSScraper(config)
    aggregator = FuelAggregator(config, scraper)

    try:
        scraper.start_browser(headless=False)
        scraper.login()

        # Collect all data
        data = aggregator.collect_all_gallons(
            week_params['start_date'],
            week_params['end_date']
        )

        print("\n=== RESULTS ===")
        print(f"Week: {week_params['week_label']}")
        print(f"Diesel: {data['diesel_gal']:,.2f}")
        print(f"Regular: {data['regular_gal']:,.2f}")
        print(f"DEF: {data['def_gal']:,.2f}")
        print(f"Total: {data['total_gal']:,.2f}")

        print("\nPrefix details:")
        for prefix, qty in data['prefix_details'].items():
            print(f"  {prefix}: {qty:,.2f}")

        # Run sanity check
        aggregator.run_sanity_check(week_params['start_date'], week_params['end_date'])

    finally:
        scraper.close()
