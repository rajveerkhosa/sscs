#!/usr/bin/env python3
"""
Quick email test - no data collection, just sends a test email
"""

import os
import logging
from dotenv import load_dotenv
from email_sender import EmailSender

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 70)
print("EMAIL TEST - Quick Test")
print("=" * 70)
print()

# Check credentials
email_user = os.getenv('EMAIL_USER')
email_pass = os.getenv('EMAIL_PASSWORD')
email_to = os.getenv('EMAIL_TO')

print(f"From: {email_user}")
print(f"To: {email_to}")
print(f"Password length: {len(email_pass)} characters")
print()

# Test email body
test_body = """SSCS WEEKLY REPORT - TEST EMAIL

This is a test email to verify your email configuration works.

Week: 2025-10-21 to 2025-10-27
Excel Row Label: Oct 28th

======================================================================
WEEKLY GALLONS 25 - FUEL DATA SUMMARY
======================================================================

                      THIS WEEK       LAST YEAR          CHANGE
----------------------------------------------------------------------
Diesel (B/C):         15,860.75       14,485.53       +1,375.22
Regular (E/F):         9,764.31       10,058.25         -293.94
DEF (H/I):               425.99          325.30         +100.69
----------------------------------------------------------------------
TOTAL (K/L):          26,051.05       24,869.08       +1,181.97

======================================================================
C STORE SALES 25 - SALES DATA SUMMARY
======================================================================

                           THIS WEEK       LAST YEAR          CHANGE
----------------------------------------------------------------------
Total C-Store (B/C): $     47,710.24 $     47,734.96 $        -24.72
Lottery (E/F):       $      4,314.00 $      4,349.00 $        -35.00
Scale (H/I):         $      2,290.75 $      1,330.99 $       +959.76
Other Sales (K/L):   $     41,105.49 $     42,054.97 $       -949.48

======================================================================

✓ If you received this email, your email configuration is working!

---
This is a test email from the SSCS Data Collection System.
"""

try:
    # Sample fuel data
    fuel_data = {
        'diesel_gal': 15860.75,
        'regular_gal': 9764.31,
        'def_gal': 425.99,
        'total_gal': 26051.05,
        'prefix_details': {
            '050': 11797.27,
            '019': 4063.48,
            '001': 7788.67,
            '002': 1058.80,
            '003': 916.84,
            '062': 425.99
        }
    }

    fuel_data_ly = {
        'diesel_gal': 14485.53,
        'regular_gal': 10058.25,
        'def_gal': 325.30,
        'total_gal': 24869.08,
        'prefix_details': {
            '050': 10701.58,
            '019': 3783.95,
            '001': 8169.34,
            '002': 928.65,
            '003': 960.26,
            '062': 325.30
        }
    }

    cstore_data = {
        'total_cstore_sales': 47710.24,
        'lottery_sales': 4314.00,
        'scale_sales': 2290.75,
        'other_sales': 41105.49,
        'dept_27': 2670.00,
        'dept_43': 591.00,
        'dept_72': 1053.00,
        'dept_88': 2290.75
    }

    cstore_data_ly = {
        'total_cstore_sales': 47734.96,
        'lottery_sales': 4349.00,
        'scale_sales': 1330.99,
        'other_sales': 42054.97,
        'dept_27': 3764.00,
        'dept_43': 0.00,
        'dept_72': 585.00,
        'dept_88': 1330.99
    }

    # Sample department sales
    dept_sales = {
        '79': 4231.59,
        '55': 0.00,
        '59': 3035.81,
        '29': 0.00,
        '2': 0.00,
        '48': 0.00,
        '4': 0.00,
        '8': 0.00,
        '63': 0.00,
        '42': 0.00,
        '66': 0.00,
        '60': 1585.56,
        '3': 1356.79,
        '30': 0.00,
        '62': 0.00,
        '40': 499.07,
        '36': 0.00,
        '49': 0.00,
        '31': 755.76,
        '16': 307.58,
        '9': 338.36,
        '39': 414.36,
        '25': 222.91
    }

    dept_names = {
        '79': 'Krispy Krunchy',
        '55': 'Beer High Desert',
        '59': 'Core mark no tax',
        '29': 'Hot Food',
        '2': 'Cigarettes',
        '48': 'Coke',
        '4': 'Beer Advance',
        '8': 'Candy',
        '63': 'Pepsi No Tax',
        '42': 'Pepsi',
        '66': 'Red Bull',
        '60': 'Frito Lay',
        '3': 'Other Tobacco',
        '30': 'Coffee',
        '62': 'Coke No Tax',
        '40': 'Bon appetit',
        '36': 'Bev Non Carb NoTax',
        '49': 'Core mark',
        '31': 'Fountain Soda',
        '16': 'Packaged sweet snack',
        '9': 'Fluid Milk Products',
        '39': 'Emery Jenson',
        '25': 'Deff Diesel Exact'
    }

    # Import the format function
    from email_sender import format_email_body

    # Generate formatted email body
    test_body = format_email_body(
        week_label="Oct 28th",
        week_range="2025-10-21 to 2025-10-27",
        fuel_data=fuel_data,
        fuel_data_ly=fuel_data_ly,
        cstore_data=cstore_data,
        cstore_data_ly=cstore_data_ly,
        dept_count=len(dept_sales),
        dept_sales=dept_sales,
        dept_names=dept_names
    )

    # Create email sender
    sender = EmailSender(logger=logger)

    print("Attempting to send test email...")
    print()

    # Send test email
    success = sender.send_weekly_report(
        recipient=email_to,
        subject="SSCS Weekly Report - EMAIL TEST (Full Format)",
        body_text=test_body,
        excel_path=None
    )

    print()
    print("=" * 70)
    if success:
        print("✓ SUCCESS! Email sent successfully!")
        print()
        print(f"Check your inbox: {email_to}")
        print("(Check spam folder if you don't see it)")
    else:
        print("✗ FAILED! Email was not sent.")
        print()
        print("Check the error messages above.")
    print("=" * 70)

except Exception as e:
    print()
    print("=" * 70)
    print(f"✗ ERROR: {e}")
    print("=" * 70)
    import traceback
    traceback.print_exc()
