import os
import requests
from datetime import datetime, timedelta

class AlphaVantageClient:
    def __init__(self):
        self.api_key = os.getenv("ALPHA_VANTAGE_API")
        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_API environment variable or api_key argument must be set.")
        self.base_url = "https://www.alphavantage.co/query"

    def _make_request(self, function, params=None):
        """Internal method to make requests to the AlphaVantage API."""

        all_params = {"function": function, "apikey": self.api_key}
        if params:
            all_params.update(params)  # Add any user-supplied parameters

        try:
            response = requests.get(self.base_url, params=all_params)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None  # Or raise the exception if you prefer

    def get_most_active_tickers(self):
        """Gets most active tickers from Alpha Vantage."""
        data = self._make_request("TOP_GAINERS_LOSERS")

        if data and 'most_actively_traded' in data: # Check if data and the key exist
            tickers = [item['ticker'] for item in data['most_actively_traded']]
            return tickers
        else:
            print("No 'most_actively_traded' data found or API returned an error.") # More specific error message
            return []
        
    def get_insider_transactions(self, ticker):
        """Gets insider transactions from the last month (max 10) for a given ticker."""

        params = {"function": "INSIDER_TRANSACTIONS", "symbol": ticker}
        raw_data = self._make_request("INSIDER_TRANSACTIONS", params)

        if raw_data and 'data' in raw_data: # Check for both raw_data and 'data' key
            today = datetime.today().date()
            one_month_ago = today - timedelta(days=30)

            recent_transactions = [
                trans for trans in raw_data['data']
                if datetime.strptime(trans['transaction_date'], '%Y-%m-%d').date() >= one_month_ago
            ]

            return recent_transactions[:10]
        else:
            print("No 'data' found in Insider Transactions response or API returned an error.")
            return []
