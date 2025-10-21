#!/usr/bin/env python3
"""
SSCS Weekly Tracker Updater
Main orchestration script - scrapes SSCS fuel data and updates Excel tracker.
"""

import os
import sys
import logging
import yaml
from datetime import datetime
from dotenv import load_dotenv

from week_utils import get_week_params
from sscs_scraper import SSCSScraper
from fuel_aggregator import FuelAggregator
from excel_updater import ExcelUpdater


def setup_logging(log_dir):
    """
    Set up logging to both file and console.

    Args:
        log_dir (str): Directory for log files

    Returns:
        logging.Logger: Configured logger
    """
    os.makedirs(log_dir, exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = os.path.join(log_dir, f'sscs_update_{timestamp}.log')

    # Configure logging
    logger = logging.getLogger('SSCS_Tracker')
    logger.setLevel(logging.INFO)

    # File handler (detailed)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler (less verbose)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logging initialized. Log file: {log_file}")

    return logger


def load_config(config_path='config.yaml'):
    """
    Load configuration from YAML file.

    Args:
        config_path (str): Path to config file

    Returns:
        dict: Configuration dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config


def main():
    """Main execution function"""

    print("=" * 60)
    print("SSCS Weekly Tracker Updater")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"ERROR: Failed to load config: {e}")
        sys.exit(1)

    # Set up logging
    log_dir = config['excel']['log_dir']
    logger = setup_logging(log_dir)

    logger.info("=" * 60)
    logger.info("SSCS Weekly Tracker Update - START")
    logger.info("=" * 60)

    scraper = None
    success = False

    try:
        # Calculate week parameters
        logger.info("Calculating week parameters...")
        week_params = get_week_params()

        logger.info(f"Week Ending: {week_params['week_label']}")
        logger.info(f"Period: {week_params['start_datetime']} to {week_params['end_datetime']}")
        logger.info(f"SSCS date range: {week_params['start_date']} - {week_params['end_date']}")

        # Initialize scraper
        logger.info("Initializing SSCS scraper...")
        scraper = SSCSScraper(config, logger)

        # Start browser and login
        logger.info("Starting browser and logging in...")
        headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        scraper.start_browser(headless=headless)
        scraper.login()

        # Initialize aggregator
        logger.info("Initializing fuel aggregator...")
        aggregator = FuelAggregator(config, scraper, logger)

        # Collect fuel data
        logger.info("Collecting fuel data from SSCS...")
        fuel_data = aggregator.collect_all_gallons(
            week_params['start_date'],
            week_params['end_date']
        )

        # Log summary
        logger.info("=" * 40)
        logger.info("FUEL DATA SUMMARY")
        logger.info("=" * 40)
        logger.info(f"Diesel:  {fuel_data['diesel_gal']:>12,.2f} gal")
        logger.info(f"Regular: {fuel_data['regular_gal']:>12,.2f} gal")
        logger.info(f"DEF:     {fuel_data['def_gal']:>12,.2f} gal")
        logger.info(f"TOTAL:   {fuel_data['total_gal']:>12,.2f} gal")
        logger.info("=" * 40)

        # Prefix breakdown
        logger.info("Prefix breakdown:")
        for prefix, qty in sorted(fuel_data['prefix_details'].items()):
            logger.info(f"  {prefix}: {qty:,.2f} gal")

        # Optional: Run sanity check
        if os.getenv('RUN_SANITY_CHECK', 'false').lower() == 'true':
            logger.info("Running pagination sanity check...")
            aggregator.run_sanity_check(
                week_params['start_date'],
                week_params['end_date']
            )

        # Close browser (we're done scraping)
        logger.info("Closing browser...")
        scraper.close()
        scraper = None

        # Update Excel
        logger.info("Updating Excel tracker...")
        updater = ExcelUpdater(config, logger)
        updater.update_tracker(week_params['week_label'], fuel_data)

        logger.info("=" * 60)
        logger.info("UPDATE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)

        success = True

    except Exception as e:
        logger.error("=" * 60)
        logger.error("UPDATE FAILED")
        logger.error("=" * 60)
        logger.error(f"Error: {e}", exc_info=True)
        success = False

    finally:
        # Cleanup
        if scraper:
            try:
                scraper.close()
            except:
                pass

    # Exit with appropriate code
    if success:
        print("\n✓ Update completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Update failed. Check logs for details.")
        sys.exit(1)


if __name__ == '__main__':
    main()
