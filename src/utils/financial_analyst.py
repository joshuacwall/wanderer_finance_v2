def format_stock_data(stock_data):
    """Format the stock data into a readable string, handling potential missing keys."""
    try:
        return f'''
- Open: {stock_data.get('Open', 'N/A')}
- High: {stock_data.get('High', 'N/A')}
- Low: {stock_data.get('Low', 'N/A')}
- Close: {stock_data.get('Close', 'N/A')}
- 52-Week High: {stock_data.get('52W_High', 'N/A')}
- 52-Week Low: {stock_data.get('52W_Low', 'N/A')}
- 200 Day Average: {stock_data.get('200DayAverage', 'N/A')}
'''
    except AttributeError:  # Handle cases where stock_data might not be a dictionary
        return "Data not available."


def format_news_articles(news_articles):
    """Format news, handling missing keys and empty list."""
    if not news_articles:
        return "No news available."

    news_str = "\n"
    for article in news_articles:
        try:
            news_str += f'''
Title: {article.get('title', 'N/A')}
Description: {article.get('description', 'N/A')}
Published Date: {article.get('pubDate', 'N/A')}
Sentiment: {article.get('sentiment', 'N/A')}
Sentiment Explanation: {article.get('sentiment_explanation', 'N/A')}
'''
        except AttributeError:  # Handle if an article is not a dictionary
            news_str += "Article data not available.\n"
    return news_str

def format_executive_sales(transactions):
    """Parse and format executive sales, handling missing keys and invalid data."""
    executive_sales = {}
    for transaction in transactions:
        try:
            if transaction.get("acquisition_or_disposal") == "D":
                executive = transaction.get("executive", "Unknown Executive")
                shares_sold = float(transaction.get("shares", 0))  # Default to 0 if shares is invalid
                if executive in executive_sales:
                    executive_sales[executive] += shares_sold
                else:
                    executive_sales[executive] = shares_sold
        except (ValueError, TypeError):  # Handle invalid 'shares' values
            print("Warning: Invalid share count in transaction.")
            continue  # Skip to the next transaction

    if not executive_sales:
        return "\nNo transactions available."

    sales_str = "\n"
    for executive, shares_sold in executive_sales.items():
        sales_str += f'''
Executive: {executive}
Total Shares Sold: {shares_sold}
'''
    return sales_str