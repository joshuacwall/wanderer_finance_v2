import requests
import os

class NewsDataClient:
    def __init__(self):
        self.api_key = os.getenv("NEWSDATA_API")
        if not self.api_key:
            raise ValueError("NEWSDATA_API environment variable or api_key argument must be set.")
        self.base_url = "https://newsdata.io/api/1/news"

    def get_ticker_news_summaries(self, ticker, num_articles=3):
        """Gets news summaries for a ticker."""

        query = f"{ticker} news"  # Construct the query

        params = {
            "q": query,
            "language": "en",
            "category": "business",
            "apikey": self.api_key,
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if data.get("status") != "success":
                print(f"Error with the news API call: {data.get('message')}")
                return []

            results = data.get('results', [])

            # Filter results based on description length
            filtered_results = [
                article for article in results
                if article.get('description') and len(article['description'].split()) > 30
            ]

            return filtered_results[:num_articles]

        except requests.exceptions.RequestException as e:  # Catch requests-specific errors
            print(f"Error fetching news: {e}")
            return []

        except Exception as e: # Catch any other errors
            print(f"An unexpected error occurred: {e}")
            return []
