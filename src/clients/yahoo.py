import yfinance as yf
import pandas as pd

def get_current_day_metrics(ticker):
    """
    Retrieves current day's metrics (Open, High, Low, Close, Volume), 200-day average,
    and 52-week high and low.

    Args:
        ticker (str): The stock ticker symbol (e.g., "AAPL", "MSFT").

    Returns:
        pandas.DataFrame: A DataFrame containing the current day's metrics, 200-day average,
                          and 52-week high/low, or None if an error occurs.
                          The DataFrame will only have one row (the current day).
        Prints an error message if the ticker is invalid or data retrieval fails.
    """
    try:
        ticker_info = yf.Ticker(ticker).info

        if not ticker_info:
            print(f"No information found for ticker {ticker}.")
            return None

        # Extract relevant metrics from ticker_info
        current_data = {
            'Open': ticker_info.get('regularMarketOpen'),
            'High': ticker_info.get('regularMarketDayHigh'),
            'Low': ticker_info.get('regularMarketDayLow'),
            'Close': ticker_info.get('regularMarketPrice'),
            'Volume': ticker_info.get('regularMarketVolume'),
            '52W_High': ticker_info.get('fiftyTwoWeekHigh'),
            '52W_Low': ticker_info.get('fiftyTwoWeekLow'),
            '200DayAverage': ticker_info.get('twoHundredDayAverage')
        }

        return current_data

    except Exception as e:
        print(f"Error retrieving data for {ticker}: {e}")
        return None
    
def get_sp500_percent_change(date):
    """
    Calculates the percent change in the S&P 500 between the given date and the last market open day before it.

    Args:
        date (str or pandas.Timestamp): The date for which to calculate the S&P 500 percent change.

    Returns:
        float or None: The percent change in the S&P 500, or None if data retrieval fails.
    """
    try:
        date = pd.to_datetime(date)  # Ensure date is a pandas Timestamp

        sp500 = yf.Ticker("^GSPC")

        # Get S&P 500 data for the given date
        current_day_data = sp500.history(start=date, end=date + pd.Timedelta(days=1))

        if current_day_data.empty:
            print(f"No S&P 500 data found for {date.strftime('%Y-%m-%d')}.")
            return None

        current_close = current_day_data['Close'].iloc[0]

        # Find the last market open day before the given date
        previous_date = date - pd.Timedelta(days=1)
        while True:
            previous_day_data = sp500.history(start=previous_date, end=previous_date + pd.Timedelta(days=1))
            if not previous_day_data.empty:
                previous_close = previous_day_data['Close'].iloc[0]
                break
            previous_date -= pd.Timedelta(days=1)

        percent_change = ((current_close - previous_close) / previous_close) * 100
        return percent_change

    except Exception as e:
        print(f"Error retrieving S&P 500 data: {e}")
        return None