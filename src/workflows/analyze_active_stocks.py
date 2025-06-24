"""
Workflow for analyzing active stocks using LLM-based analysis.

This module provides the main workflow for analyzing the most active stocks,
gathering data from multiple sources, and generating trading recommendations.
"""

from typing import List, Optional
import pandas as pd
from datetime import datetime

from src.clients.advantage import AlphaVantageClient
from src.clients.new_data import NewsDataClient
from src.clients.yahoo import get_current_day_metrics
from src.agents import zero_shot_agent
from src.utils.financial_analyst import format_stock_data, format_news_articles, format_executive_sales
from src.utils.json_parser import parse_llm_output
from src.utils.logging_config import get_logger
from src.utils.models import AnalysisResult, SentimentResult
from src.config import config
from src.constants import TradingAction, MAX_ARTICLES_PER_STOCK

logger = get_logger(__name__)


def analyze_active_stocks(
    model: str = None,
    temperature: float = None,
    max_stocks: Optional[int] = None
) -> pd.DataFrame:
    """
    Automates the analysis of most active stocks and stores results in a DataFrame.

    Args:
        model: LLM model to use for analysis. Defaults to config value.
        temperature: Temperature for LLM. Defaults to config value.
        max_stocks: Maximum number of stocks to analyze. None for all.

    Returns:
        DataFrame with tickers and their analysis results.

    Raises:
        ValueError: If no tickers are retrieved or analysis fails.
    """
    # Use config defaults if not provided
    model = model or config.llm.model
    temperature = temperature if temperature is not None else config.llm.temperature

    logger.info(f"Starting stock analysis with model: {model}, temperature: {temperature}")

    try:
        # Get active tickers
        alpha_vantage_client = AlphaVantageClient()
        tickers = alpha_vantage_client.get_most_active_tickers()

        if not tickers:
            raise ValueError("Failed to retrieve active tickers")

        # Limit number of stocks if specified
        if max_stocks:
            tickers = tickers[:max_stocks]

        logger.info(f"Retrieved {len(tickers)} tickers for analysis: {tickers}")

        current_date = datetime.today().date()
        results = []

        # Process each ticker
        for ticker in tickers:
            try:
                result = _analyze_single_stock(
                    ticker=ticker,
                    model=model,
                    temperature=temperature,
                    current_date=current_date
                )
                if result:
                    results.append(result)

            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}", exc_info=True)
                continue

        # Convert results to DataFrame
        results_df = pd.DataFrame(results)
        logger.info(f"Analysis completed. Processed {len(results_df)} stocks successfully.")

        return results_df

    except Exception as e:
        logger.error(f"Error in analyze_active_stocks: {e}", exc_info=True)
        raise


def _analyze_single_stock(
    ticker: str,
    model: str,
    temperature: float,
    current_date: datetime
) -> Optional[dict]:
    """
    Analyze a single stock and return the analysis result.

    Args:
        ticker: Stock ticker symbol
        model: LLM model to use
        temperature: LLM temperature
        current_date: Current date for the analysis

    Returns:
        Dictionary with analysis results or None if analysis fails
    """
    logger.info(f"Processing ticker: {ticker}")

    try:
        # Gather news data
        news_client = NewsDataClient()
        articles = news_client.get_ticker_news_summaries(
            ticker,
            num_articles=config.trading.max_articles_per_stock
        )

        # Process articles with sentiment analysis
        formatted_articles, article_links_and_sentiments = _process_articles(
            articles=articles,
            ticker=ticker,
            model=model,
            temperature=temperature
        )

        # Get stock data
        stock_data = get_current_day_metrics(ticker)
        previous_close = _extract_previous_close(stock_data, ticker)
        formatted_stock_info = format_stock_data(stock_data)

        # Get insider trading data
        alpha_vantage_client = AlphaVantageClient()
        insider_transactions = alpha_vantage_client.get_insider_transactions(ticker)
        formatted_insider_transactions = format_executive_sales(insider_transactions)

        # Perform LLM analysis
        analysis_result = _perform_llm_analysis(
            ticker=ticker,
            stock_analysis=formatted_stock_info,
            recent_news=formatted_articles,
            insider_transactions=formatted_insider_transactions,
            model=model,
            temperature=temperature
        )

        # Return structured result
        return {
            'ticker': ticker,
            'action': analysis_result["action"],
            'explanation': analysis_result["explanation"],
            'record_date': current_date,
            'article_links_and_sentiments': str(article_links_and_sentiments),
            "previous_close": previous_close
        }

    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}", exc_info=True)
        return None


def _process_articles(
    articles: List[dict],
    ticker: str,
    model: str,
    temperature: float
) -> tuple[str, List[dict]]:
    """
    Process articles with sentiment analysis.

    Args:
        articles: List of article dictionaries
        ticker: Stock ticker symbol
        model: LLM model to use
        temperature: LLM temperature

    Returns:
        Tuple of (formatted_articles_string, article_links_and_sentiments)
    """
    formatted_articles = []
    article_links_and_sentiments = []

    for article in articles:
        try:
            user_vars_sentiment = {
                "summary": article.get("description", ""),
                "title": article.get("title", "")
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
            article_links_and_sentiments.append({
                'link': link,
                'sentiment': sentiment
            })

        except Exception as e:
            logger.warning(f"Error processing article for {ticker}: {e}")
            continue

    formatted_articles_str = format_news_articles(formatted_articles)
    return formatted_articles_str, article_links_and_sentiments


def _extract_previous_close(stock_data: Optional[dict], ticker: str) -> Optional[float]:
    """
    Extract previous close price from stock data.

    Args:
        stock_data: Stock data dictionary
        ticker: Stock ticker symbol

    Returns:
        Previous close price or None if not available
    """
    if stock_data is not None:
        previous_close = stock_data.get('Close')
        if previous_close is not None:
            logger.info(f"Close value for {ticker}: {previous_close}")
            return previous_close
        else:
            logger.warning(f"Close value not found for {ticker}")
    else:
        logger.warning(f"No stock data available for {ticker}")

    return None


def _perform_llm_analysis(
    ticker: str,
    stock_analysis: str,
    recent_news: str,
    insider_transactions: str,
    model: str,
    temperature: float
) -> dict:
    """
    Perform LLM-based financial analysis.

    Args:
        ticker: Stock ticker symbol
        stock_analysis: Formatted stock data
        recent_news: Formatted news articles
        insider_transactions: Formatted insider trading data
        model: LLM model to use
        temperature: LLM temperature

    Returns:
        Dictionary with analysis results

    Raises:
        ValueError: If analysis fails or returns invalid results
    """
    user_vars = {
        "ticker": ticker,
        "stock_analysis": stock_analysis,
        "recent_news": recent_news,
        "insider_transactions": insider_transactions,
    }

    try:
        response = zero_shot_agent.invoke_agent(
            user_variables=user_vars,
            prompt_name="finance_analyst",
            model=model,
            temperature=temperature
        )

        content = response['messages'][1].content
        json_response = parse_llm_output(content, AnalysisResult)

        # Validate the response
        if not json_response.get("explanation") or not json_response.get("action"):
            raise ValueError("Invalid analysis response: missing explanation or action")

        # Validate action is a known trading action
        action = json_response["action"].upper()
        if action not in [ta.value for ta in TradingAction]:
            logger.warning(f"Unknown trading action '{action}' for {ticker}, defaulting to HOLD")
            json_response["action"] = TradingAction.HOLD.value

        return json_response

    except Exception as e:
        logger.error(f"Error in LLM analysis for {ticker}: {e}")
        raise ValueError(f"Failed to analyze {ticker}: {e}")
