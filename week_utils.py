"""
Week calculation utilities for SSCS tracker.
Handles last full Sunday calculation, date formatting, and ordinal labels.
"""

from datetime import datetime, timedelta


def get_ordinal_suffix(day):
    """
    Get ordinal suffix for a day (1st, 2nd, 3rd, 4th, etc.)

    Args:
        day (int): Day of month (1-31)

    Returns:
        str: Ordinal suffix (st, nd, rd, th)
    """
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return suffix


def format_week_label(date):
    """
    Format date as month + ordinal day (e.g., 'Oct 20th')

    Args:
        date (datetime): Date to format

    Returns:
        str: Formatted label like 'Oct 20th'
    """
    day = date.day
    suffix = get_ordinal_suffix(day)
    month_abbrev = date.strftime('%b')
    return f"{month_abbrev} {day}{suffix}"


def get_last_full_week():
    """
    Calculate the last full week (Monday through Sunday).
    Returns the most recent week that has ENDED (last Sunday).
    Week label uses the Sunday ending date.

    Returns:
        tuple: (start_datetime, end_datetime, week_label)
            - start_datetime: Monday 00:00:00
            - end_datetime: Sunday 23:59:59
            - week_label: Formatted as 'Oct 19th' (for the Sunday ending)
    """
    now = datetime.now()

    # Find the most recent Sunday that has passed
    # weekday(): Mon=0, Tue=1, ..., Sun=6
    if now.weekday() == 6:
        # Today is Sunday - use today as the week ending
        last_sunday = now
    else:
        # Go back to the most recent Sunday
        days_since_sunday = (now.weekday() + 1) % 7
        if days_since_sunday == 0:
            days_since_sunday = 7
        last_sunday = now - timedelta(days=days_since_sunday)

    # Set to end of Sunday (23:59:59)
    end_datetime = last_sunday.replace(hour=23, minute=59, second=59, microsecond=0)

    # Calculate the Monday of that week (6 days before Sunday)
    last_monday = last_sunday - timedelta(days=6)
    start_datetime = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)

    # Create week label from the Sunday ending date
    week_label = format_week_label(last_sunday)

    return start_datetime, end_datetime, week_label


def format_sscs_datetime(dt):
    """
    Format datetime for SSCS query parameters (YYYYMMDDhhmmss)

    Args:
        dt (datetime): Datetime to format

    Returns:
        str: Formatted as YYYYMMDDhhmmss (e.g., '20250721000000')
    """
    return dt.strftime('%Y%m%d%H%M%S')


def get_last_year_week(week_ending_sunday):
    """
    Calculate the corresponding week from last year.

    Given a Sunday date (week ending), finds the week in the previous year
    that contains the same date (one year ago).

    Example:
        - Input: Oct 19, 2025 (Sunday)
        - Same date last year: Oct 19, 2024 (Saturday)
        - Week containing Oct 19, 2024: Oct 14-20, 2024 (Mon-Sun)

    Args:
        week_ending_sunday (datetime): The Sunday that ends the current week

    Returns:
        tuple: (start_datetime, end_datetime)
            - start_datetime: Monday 00:00:00 of last year's week
            - end_datetime: Sunday 23:59:59 of last year's week
    """
    # Go back exactly one year from the Sunday
    same_date_last_year = week_ending_sunday.replace(year=week_ending_sunday.year - 1)

    # Find which day of the week it was
    weekday = same_date_last_year.weekday()  # Mon=0, Sun=6

    # Calculate the Monday and Sunday of that week
    if weekday == 6:
        # It was a Sunday - this IS the week ending
        last_year_sunday = same_date_last_year
    else:
        # Find the next Sunday after this date
        days_until_sunday = (6 - weekday) % 7
        if days_until_sunday == 0:
            days_until_sunday = 7
        last_year_sunday = same_date_last_year + timedelta(days=days_until_sunday)

    # Calculate Monday (6 days before Sunday)
    last_year_monday = last_year_sunday - timedelta(days=6)

    # Set proper times
    start_datetime = last_year_monday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_datetime = last_year_sunday.replace(hour=23, minute=59, second=59, microsecond=0)

    return start_datetime, end_datetime


def get_week_params():
    """
    Get all week-related parameters for SSCS queries, including last year.

    Returns:
        dict: {
            'start_date': 'YYYYMMDDhhmmss',
            'end_date': 'YYYYMMDDhhmmss',
            'week_label': 'DDth MMM',
            'start_datetime': datetime,
            'end_datetime': datetime,
            'ly_start_date': 'YYYYMMDDhhmmss',
            'ly_end_date': 'YYYYMMDDhhmmss',
            'ly_start_datetime': datetime,
            'ly_end_datetime': datetime
        }
    """
    start_dt, end_dt, week_label = get_last_full_week()

    # Get last year's corresponding week
    ly_start_dt, ly_end_dt = get_last_year_week(end_dt)

    return {
        'start_date': format_sscs_datetime(start_dt),
        'end_date': format_sscs_datetime(end_dt),
        'week_label': week_label,
        'start_datetime': start_dt,
        'end_datetime': end_dt,
        'ly_start_date': format_sscs_datetime(ly_start_dt),
        'ly_end_date': format_sscs_datetime(ly_end_dt),
        'ly_start_datetime': ly_start_dt,
        'ly_end_datetime': ly_end_dt
    }


if __name__ == '__main__':
    # Test the week calculation
    params = get_week_params()
    print(f"Week Label: {params['week_label']}")
    print(f"Start: {params['start_datetime']} -> {params['start_date']}")
    print(f"End: {params['end_datetime']} -> {params['end_date']}")
