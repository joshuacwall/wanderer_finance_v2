import datetime
import holidays

def is_us_market_open(date=None):
    """Checks if the US stock market is open on a given date.

    Args:
        date: datetime.date object. If None, defaults to today.

    Returns:
        True if the market is open, False otherwise.
    """
    if date is None:
        date = datetime.date.today()

    us_holidays = holidays.US()  # Get US holidays

    # Weekends
    if date.weekday() in (5, 6):  # Saturday or Sunday
        return False

    # Holidays
    if date in us_holidays:
        return False

    return True