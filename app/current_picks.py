"""
Current stock picks tab for Wanderer Finance Gradio interface.

This module provides the interface for viewing current stock recommendations,
including real-time price data and LLM-generated explanations.
"""

from typing import Optional, Tuple
import gradio as gr
import pandas as pd
import yfinance as yf
from datetime import datetime

from src.clients.sqllite import SQLiteClient
from src.config import config
from src.utils.logging_config import get_logger
from src.constants import DEFAULT_TICKER_OPTION, REFRESH_BUTTON_TEXT, TradingAction

logger = get_logger(__name__)

# SQL query to get current BUY recommendations
CURRENT_PICKS_QUERY = """
SELECT ticker, record_date, action, explanation
FROM data
WHERE record_date = (SELECT MAX(record_date) FROM data)
AND action = ?
ORDER BY ticker ASC
"""

def create_tab() -> gr.TabItem:
    """
    Create the current stock picks tab.

    Returns:
        Configured Gradio TabItem
    """
    with gr.TabItem("Current Stock Picks"):
        gr.Markdown(
            """
            ### 📈 Current Stock Recommendations
            View the latest AI-generated stock picks with real-time pricing and analysis.
            """
        )

        with gr.Row():
            # Left column - Stock list and selection
            with gr.Column(scale=1):
                refresh_button = gr.Button(
                    REFRESH_BUTTON_TEXT,
                    variant="primary",
                    size="sm"
                )

                output_table = gr.DataFrame(
                    label="Current BUY Recommendations",
                    headers=["Ticker", "Date", "Action"],
                    datatype=["str", "str", "str"],
                    interactive=False
                )

                ticker_dropdown = gr.Dropdown(
                    choices=[DEFAULT_TICKER_OPTION],
                    label="Select a Ticker for Details",
                    value=DEFAULT_TICKER_OPTION,
                    interactive=True
                )

            # Right column - Stock details
            with gr.Column(scale=2):
                with gr.Group():
                    gr.Markdown("#### Stock Details")

                    date_text = gr.Textbox(
                        label="📅 Analysis Date",
                        interactive=False,
                        placeholder="Select a ticker to view details"
                    )

                    price_text = gr.Textbox(
                        label="💰 Current Price (Yahoo Finance)",
                        interactive=False,
                        placeholder="Real-time price will appear here"
                    )

                    action_text = gr.Textbox(
                        label="🎯 Recommended Action",
                        interactive=False,
                        placeholder="AI recommendation will appear here"
                    )

                    additional_data_text = gr.Textbox(
                        label="🤖 AI Analysis Explanation",
                        lines=8,
                        interactive=False,
                        placeholder="Detailed AI analysis will appear here"
                    )

        # Event handlers
        def refresh_table() -> pd.DataFrame:
            """Refresh the stock picks table."""
            try:
                logger.info("Refreshing stock picks table")

                with SQLiteClient() as client:
                    results = client.query(CURRENT_PICKS_QUERY, params=[TradingAction.BUY.value])

                if results is not None and not results.empty:
                    # Select only the columns we want to display
                    display_df = results[['ticker', 'record_date', 'action']].copy()
                    logger.info(f"Retrieved {len(display_df)} current picks")
                    return display_df
                else:
                    logger.warning("No current picks found")
                    return pd.DataFrame({"Message": ["No current picks available"]})

            except Exception as e:
                logger.error(f"Error refreshing table: {e}")
                return pd.DataFrame({"Error": [f"Failed to load data: {str(e)}"]})

        def get_stock_details(selected_ticker: str) -> Tuple[str, str, str, str]:
            """
            Get detailed information for selected stock.

            Args:
                selected_ticker: Selected ticker symbol

            Returns:
                Tuple of (date, price, action, explanation)
            """
            if selected_ticker == DEFAULT_TICKER_OPTION:
                return "", "", "", "Please select a ticker from the dropdown."

            try:
                logger.info(f"Getting details for ticker: {selected_ticker}")

                # Get current price
                price_display = _get_current_price(selected_ticker)

                # Get analysis data
                date_text, action_text, explanation_text = _get_analysis_data(selected_ticker)

                return date_text, price_display, action_text, explanation_text

            except Exception as e:
                logger.error(f"Error fetching data for {selected_ticker}: {e}")
                return "Error", "Error fetching price", "Error", f"Error: {str(e)}"

        def update_dropdown_choices() -> Tuple[pd.DataFrame, gr.Dropdown]:
            """Update both table and dropdown choices."""
            df = refresh_table()

            # Extract ticker choices
            if not df.empty and 'ticker' in df.columns:
                ticker_choices = [DEFAULT_TICKER_OPTION] + df['ticker'].tolist()
            else:
                ticker_choices = [DEFAULT_TICKER_OPTION]

            # Update dropdown
            updated_dropdown = gr.Dropdown(
                choices=ticker_choices,
                value=DEFAULT_TICKER_OPTION
            )

            return df, updated_dropdown

        # Initialize with data
        initial_df = refresh_table()
        output_table.value = initial_df

        # Set up event handlers
        refresh_button.click(
            fn=update_dropdown_choices,
            outputs=[output_table, ticker_dropdown]
        )

        ticker_dropdown.change(
            fn=get_stock_details,
            inputs=[ticker_dropdown],
            outputs=[date_text, price_text, action_text, additional_data_text]
        )


def _get_current_price(ticker: str) -> str:
    """
    Get current stock price from Yahoo Finance.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Formatted price string
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Try different price fields
        current_price = (
            info.get('regularMarketPrice') or
            info.get('currentPrice') or
            info.get('previousClose')
        )

        if current_price and isinstance(current_price, (int, float)):
            return f"${current_price:.2f}"
        else:
            return "Price not available"

    except Exception as e:
        logger.warning(f"Error getting price for {ticker}: {e}")
        return "Error fetching price"


def _get_analysis_data(ticker: str) -> Tuple[str, str, str]:
    """
    Get analysis data for a ticker from database.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Tuple of (date, action, explanation)
    """
    try:
        query = """
        SELECT explanation, action, record_date
        FROM data
        WHERE ticker = ? AND record_date = (SELECT MAX(record_date) FROM data)
        """

        with SQLiteClient() as client:
            df = client.query(query, params=[ticker])

        if df is not None and not df.empty:
            row = df.iloc[0]
            return (
                str(row['record_date']),
                str(row['action']),
                str(row['explanation'])
            )
        else:
            return (
                "No data found",
                "No action found",
                f"No analysis found for {ticker} in the most recent data."
            )

    except Exception as e:
        logger.error(f"Error getting analysis data for {ticker}: {e}")
        return (
            "Error",
            "Error",
            f"Error retrieving analysis: {str(e)}"
        )