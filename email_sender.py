#!/usr/bin/env python3
"""
Email sender for SSCS Weekly Reports.
Sends formatted emails with Excel attachments via Outlook/Office365.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import logging


class EmailSender:
    """Send emails via Outlook/Office365 SMTP"""

    def __init__(self, email_user=None, email_password=None, logger=None):
        """
        Initialize email sender.

        Args:
            email_user (str): Sender email address (Outlook/Office365)
            email_password (str): Email password or app password
            logger: Logger instance
        """
        self.email_user = email_user or os.getenv('EMAIL_USER')
        self.email_password = email_password or os.getenv('EMAIL_PASSWORD')
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.logger = logger or logging.getLogger(__name__)

        if not self.email_user or not self.email_password:
            raise ValueError("Email credentials not found. Set EMAIL_USER and EMAIL_PASSWORD in .env file")

    def send_weekly_report(self, recipient, subject, body_text, excel_path=None):
        """
        Send weekly report email.

        Args:
            recipient (str): Recipient email address
            subject (str): Email subject
            body_text (str): Plain text email body
            excel_path (str): Path to Excel attachment (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = recipient
            msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(body_text, 'plain'))

            # Add Excel attachment if provided
            if excel_path and os.path.exists(excel_path):
                with open(excel_path, 'rb') as f:
                    excel_data = f.read()

                attachment = MIMEApplication(excel_data, _subtype='xlsx')
                attachment.add_header('Content-Disposition', 'attachment',
                                     filename=os.path.basename(excel_path))
                msg.attach(attachment)
                self.logger.info(f"Attached Excel file: {os.path.basename(excel_path)}")
            else:
                self.logger.info("No Excel attachment (text-only email)")

            # Connect and send
            self.logger.info(f"Connecting to {self.smtp_server}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                self.logger.info("Logging in...")
                server.login(self.email_user, self.email_password)

                self.logger.info(f"Sending email to {recipient}...")
                server.send_message(msg)

            self.logger.info("✓ Email sent successfully!")
            return True

        except smtplib.SMTPAuthenticationError:
            self.logger.error("Authentication failed. Check your email and password.")
            self.logger.error("For Gmail, you need to:")
            self.logger.error("  1. Go to https://myaccount.google.com/apppasswords")
            self.logger.error("  2. Create an App Password for 'Mail'")
            self.logger.error("  3. Use that 16-character password in .env file")
            return False

        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error occurred: {e}")
            return False

        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            import traceback
            traceback.print_exc()
            return False


def format_email_body(week_label, week_range, fuel_data, fuel_data_ly, cstore_data, cstore_data_ly, dept_count=0, dept_sales=None, dept_names=None):
    """
    Format plain text email body with summary data.

    Args:
        week_label (str): Week label (e.g., "Sep 29th")
        week_range (str): Week date range
        fuel_data (dict): This week's fuel data
        fuel_data_ly (dict): Last year's fuel data
        cstore_data (dict): This week's C-Store data
        cstore_data_ly (dict): Last year's C-Store data
        dept_count (int): Number of departments scraped
        dept_sales (dict): Department sales data {dept_num: sales}
        dept_names (dict): Department names {dept_num: name}

    Returns:
        str: Formatted email body
    """
    body = f"""SSCS WEEKLY REPORT
Week: {week_range}
Excel Row Label: {week_label}
Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}

{'=' * 70}
WEEKLY GALLONS 25 - FUEL DATA SUMMARY
{'=' * 70}

                      THIS WEEK       LAST YEAR          CHANGE
----------------------------------------------------------------------
Diesel (B/C):     {fuel_data['diesel_gal']:>15,.2f} {fuel_data_ly['diesel_gal']:>15,.2f} {fuel_data['diesel_gal'] - fuel_data_ly['diesel_gal']:>+15,.2f}
Regular (E/F):    {fuel_data['regular_gal']:>15,.2f} {fuel_data_ly['regular_gal']:>15,.2f} {fuel_data['regular_gal'] - fuel_data_ly['regular_gal']:>+15,.2f}
DEF (H/I):        {fuel_data['def_gal']:>15,.2f} {fuel_data_ly['def_gal']:>15,.2f} {fuel_data['def_gal'] - fuel_data_ly['def_gal']:>+15,.2f}
----------------------------------------------------------------------
TOTAL (K/L):      {fuel_data['total_gal']:>15,.2f} {fuel_data_ly['total_gal']:>15,.2f} {fuel_data['total_gal'] - fuel_data_ly['total_gal']:>+15,.2f}

FUEL BREAKDOWN BY PREFIX:
----------------------------------------------------------------------
DIESEL:
  Prefix 050:     {fuel_data['prefix_details'].get('050', 0):>15,.2f} {fuel_data_ly['prefix_details'].get('050', 0):>15,.2f} {fuel_data['prefix_details'].get('050', 0) - fuel_data_ly['prefix_details'].get('050', 0):>+15,.2f}
  Prefix 019:     {fuel_data['prefix_details'].get('019', 0):>15,.2f} {fuel_data_ly['prefix_details'].get('019', 0):>15,.2f} {fuel_data['prefix_details'].get('019', 0) - fuel_data_ly['prefix_details'].get('019', 0):>+15,.2f}

REGULAR GAS:
  Prefix 001:     {fuel_data['prefix_details'].get('001', 0):>15,.2f} {fuel_data_ly['prefix_details'].get('001', 0):>15,.2f} {fuel_data['prefix_details'].get('001', 0) - fuel_data_ly['prefix_details'].get('001', 0):>+15,.2f}
  Prefix 002:     {fuel_data['prefix_details'].get('002', 0):>15,.2f} {fuel_data_ly['prefix_details'].get('002', 0):>15,.2f} {fuel_data['prefix_details'].get('002', 0) - fuel_data_ly['prefix_details'].get('002', 0):>+15,.2f}
  Prefix 003:     {fuel_data['prefix_details'].get('003', 0):>15,.2f} {fuel_data_ly['prefix_details'].get('003', 0):>15,.2f} {fuel_data['prefix_details'].get('003', 0) - fuel_data_ly['prefix_details'].get('003', 0):>+15,.2f}

DEF:
  Prefix 062:     {fuel_data['prefix_details'].get('062', 0):>15,.2f} {fuel_data_ly['prefix_details'].get('062', 0):>15,.2f} {fuel_data['prefix_details'].get('062', 0) - fuel_data_ly['prefix_details'].get('062', 0):>+15,.2f}

{'=' * 70}
C STORE SALES 25 - SALES DATA SUMMARY
{'=' * 70}

                           THIS WEEK       LAST YEAR          CHANGE
----------------------------------------------------------------------
Total C-Store (B/C): ${cstore_data['total_cstore_sales']:>14,.2f} ${cstore_data_ly['total_cstore_sales']:>14,.2f} ${cstore_data['total_cstore_sales'] - cstore_data_ly['total_cstore_sales']:>+14,.2f}
Lottery (E/F):       ${cstore_data['lottery_sales']:>14,.2f} ${cstore_data_ly['lottery_sales']:>14,.2f} ${cstore_data['lottery_sales'] - cstore_data_ly['lottery_sales']:>+14,.2f}
Scale (H/I):         ${cstore_data['scale_sales']:>14,.2f} ${cstore_data_ly['scale_sales']:>14,.2f} ${cstore_data['scale_sales'] - cstore_data_ly['scale_sales']:>+14,.2f}
Other Sales (K/L):   ${cstore_data['other_sales']:>14,.2f} ${cstore_data_ly['other_sales']:>14,.2f} ${cstore_data['other_sales'] - cstore_data_ly['other_sales']:>+14,.2f}

LOTTERY BREAKDOWN BY DEPARTMENT:
----------------------------------------------------------------------
  Dept 27:           ${cstore_data.get('dept_27', 0):>14,.2f} ${cstore_data_ly.get('dept_27', 0):>14,.2f} ${cstore_data.get('dept_27', 0) - cstore_data_ly.get('dept_27', 0):>+14,.2f}
  Dept 43:           ${cstore_data.get('dept_43', 0):>14,.2f} ${cstore_data_ly.get('dept_43', 0):>14,.2f} ${cstore_data.get('dept_43', 0) - cstore_data_ly.get('dept_43', 0):>+14,.2f}
  Dept 72:           ${cstore_data.get('dept_72', 0):>14,.2f} ${cstore_data_ly.get('dept_72', 0):>14,.2f} ${cstore_data.get('dept_72', 0) - cstore_data_ly.get('dept_72', 0):>+14,.2f}

SCALE:
  Dept 88:           ${cstore_data.get('dept_88', 0):>14,.2f} ${cstore_data_ly.get('dept_88', 0):>14,.2f} ${cstore_data.get('dept_88', 0) - cstore_data_ly.get('dept_88', 0):>+14,.2f}

{'=' * 70}
"""

    # Department Sales Section
    if dept_count > 0 and dept_sales and dept_names:
        body += f"\n{'=' * 70}\n"
        body += f"WEEKLY DEPARTMENT SALES ({dept_count} departments)\n"
        body += f"{'=' * 70}\n\n"

        total_dept_sales = sum(dept_sales.values())
        body += f"TOTAL: ${total_dept_sales:,.2f}\n\n"
        body += f"Top 10 Departments:\n"
        body += f"{'-' * 70}\n"

        # Sort departments by sales (highest first) and show top 10
        sorted_depts = sorted(dept_sales.items(), key=lambda x: x[1], reverse=True)[:10]
        for dept_num, sales in sorted_depts:
            dept_name = dept_names.get(dept_num, "Unknown")
            body += f"  Dept {dept_num:>3} - {dept_name:<30} ${sales:>12,.2f}\n"

        body += f"\n{'=' * 70}\n"

    # Copy-Paste Section for Excel
    body += f"\n{'=' * 70}\n"
    body += "COPY-PASTE VALUES FOR EXCEL\n"
    body += f"{'=' * 70}\n\n"

    body += "--- WEEKLY GALLONS 25 ---\n"
    body += f"Excel Row Label: {week_label}\n\n"
    body += "THIS WEEK (Columns B, E, H, K):\n"
    body += f"{fuel_data['diesel_gal']:.2f}\n"
    body += f"{fuel_data['regular_gal']:.2f}\n"
    body += f"{fuel_data['def_gal']:.2f}\n"
    body += f"{fuel_data['total_gal']:.2f}\n\n"

    body += "LAST YEAR (Columns C, F, I, L):\n"
    body += f"{fuel_data_ly['diesel_gal']:.2f}\n"
    body += f"{fuel_data_ly['regular_gal']:.2f}\n"
    body += f"{fuel_data_ly['def_gal']:.2f}\n"
    body += f"{fuel_data_ly['total_gal']:.2f}\n\n"

    body += "--- C STORE SALES 25 ---\n"
    body += f"Excel Row Label: {week_label}\n\n"
    body += "THIS WEEK (Columns B, E, H, K):\n"
    body += f"{cstore_data['total_cstore_sales']:.2f}\n"
    body += f"{cstore_data['lottery_sales']:.2f}\n"
    body += f"{cstore_data['scale_sales']:.2f}\n"
    body += f"{cstore_data['other_sales']:.2f}\n\n"

    body += "LAST YEAR (Columns C, F, I, L):\n"
    body += f"{cstore_data_ly['total_cstore_sales']:.2f}\n"
    body += f"{cstore_data_ly['lottery_sales']:.2f}\n"
    body += f"{cstore_data_ly['scale_sales']:.2f}\n"
    body += f"{cstore_data_ly['other_sales']:.2f}\n\n"

    # Department sales copy-paste
    if dept_count > 0 and dept_sales:
        body += "--- WEEKLY DEPARTMENT SALES ---\n"
        body += f"Column Header: {week_label}\n\n"
        body += "Department Sales (paste into new column):\n"

        # Sort by department number
        for dept_num in sorted(dept_sales.keys(), key=lambda x: int(x)):
            sales = dept_sales[dept_num]
            body += f"{sales:.2f}\n"

        total_dept_sales = sum(dept_sales.values())
        body += f"\nTotal: {total_dept_sales:.2f}\n\n"

    body += f"{'=' * 70}\n\n"

    body += """
---
This is an automated weekly report from the SSCS Data Collection System.
Excel values are ready to copy-paste into your tracking spreadsheets.
"""

    return body


if __name__ == '__main__':
    # Test the email sender
    from dotenv import load_dotenv

    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    logger = logging.getLogger(__name__)

    # Test with sample data
    fuel_data = {
        'diesel_gal': 15860.75,
        'regular_gal': 9764.31,
        'def_gal': 425.99,
        'total_gal': 26051.05
    }

    fuel_data_ly = {
        'diesel_gal': 14485.53,
        'regular_gal': 10058.25,
        'def_gal': 325.30,
        'total_gal': 24869.08
    }

    cstore_data = {
        'total_cstore_sales': 47710.24,
        'lottery_sales': 4314.00,
        'scale_sales': 2290.75,
        'other_sales': 41105.49
    }

    cstore_data_ly = {
        'total_cstore_sales': 47734.96,
        'lottery_sales': 4349.00,
        'scale_sales': 1330.99,
        'other_sales': 42054.97
    }

    body = format_email_body(
        "Sep 29th",
        "2025-09-22 to 2025-09-28",
        fuel_data,
        fuel_data_ly,
        cstore_data,
        cstore_data_ly,
        dept_count=59
    )

    print("Email body preview:")
    print(body)

    recipient = os.getenv('EMAIL_TO')
    if recipient:
        sender = EmailSender(logger=logger)
        success = sender.send_weekly_report(
            recipient=recipient,
            subject="SSCS Weekly Report - Sep 29th",
            body_text=body
        )

        if success:
            print("\n✓ Test email sent successfully!")
        else:
            print("\n✗ Failed to send test email")
    else:
        print("\nTo send a test email, set EMAIL_TO in your .env file")
