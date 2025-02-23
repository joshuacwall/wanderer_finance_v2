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