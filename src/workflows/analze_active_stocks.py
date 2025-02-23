from src.clients.advantage import AlphaVantageClient
from src.clients.new_data import NewsDataClient
from src.clients.yahoo import get_current_day_metrics
from src.agents import zero_shot_agent
from src.utils.financial_analyst import format_stock_data, format_news_articles, format_executive_sales
from src.utils.json_parser import parse_llm_output
import datetime
import pandas as pd
from datetime import datetime
import logging
from src.utils.models import AnalysisResult, SentimentResult


def analyze_active_stocks(model = "groq/deepseek-r1-distill-llama-70b", temperature=0.1 ):
    """
    Automates the analysis of most active stocks and stores results in a DataFrame.
    Returns a DataFrame with tickers and their analysis results.
    """
    # Initialize logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Get active tickers
    tickers = AlphaVantageClient().get_most_active_tickers()  # Assuming this function is defined elsewhere
    #tickers =["NVDA"]
    current_date = datetime.today().date()
    if not tickers:
        logger.error("Failed to retrieve tickers")
        return pd.DataFrame()

    # Initialize results storage
    results = []

    # Process each ticker
    for ticker in tickers:
        try:
            logger.info(f"Processing ticker: {ticker}")
            # Gather data (your existing data collection code)
            articles = NewsDataClient().get_ticker_news_summaries(ticker, num_articles=2)
            # Use zero_shot_agent for article sentiment analysis
            formatted_articles = []
            article_links_and_sentiments = [] 
            for article in articles:
                user_vars_sentiment = {
                    "summary": article.get("description"),
                    "title": article.get("title")
                }
                sys_vars_sentiment = {
                    "ticker": ticker,
                }
                sentiment_response = zero_shot_agent.invoke_agent(
                    user_variables=user_vars_sentiment,
                    system_variables=sys_vars_sentiment,
                    prompt_name="article_sentiment",
                    model=model,
                    temperature=temperature
                )
                content = sentiment_response['messages'][1].content
                json_response = parse_llm_output(content, SentimentResult)
                article_with_sentiment = {**article, **json_response}
                formatted_articles.append(article_with_sentiment)

                # Extract link and sentiment
                link = article_with_sentiment.get('link')
                sentiment = article_with_sentiment.get('sentiment')
                article_links_and_sentiments.append({'link': link, 'sentiment': sentiment}) #add to list.
                
            formatted_articles = format_news_articles(formatted_articles)
            stock_data = get_current_day_metrics(ticker)

            # Extract Close Value (Dynamically)
            if stock_data is not None:
                previous_close = stock_data.get('Close')  # Directly get Close

                if previous_close is not None:
                    logger.info(f"Close Value for {ticker}: {previous_close}")
                else:
                    logger.info(f"Close Value not found for {ticker}")
            else:
                previous_close = None
            formatted_stock_info = format_stock_data(stock_data)

            insider_transaction = AlphaVantageClient().get_insider_transactions(ticker)
            formated_insider_transactions = format_executive_sales(insider_transaction)

            user_vars = {
                "ticker": ticker,
                "stock_analysis": formatted_stock_info,
                "recent_news": formatted_articles,
                "insider_transactions": formated_insider_transactions,
            }

            # Get analysis
            response = zero_shot_agent.invoke_agent(user_variables=user_vars, prompt_name="finance_analyst", model=model, temperature=temperature)
            content = response['messages'][1].content 
            json_response = parse_llm_output(content, AnalysisResult)

            # Extract explanation and action
            explanation = json_response["explanation"]
            action = json_response["action"]
                        
            # Store results
            results.append({
                'ticker': ticker,
                'action': action,
                'explanation': explanation,
                'current_date': current_date,
                'article_links_and_sentiments': str(article_links_and_sentiments),
                "previous_close": previous_close,
                "current_close" : None,
                "percent_change" : None,
                "evaluation" : None
            })

        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")
            continue

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    return results_df
