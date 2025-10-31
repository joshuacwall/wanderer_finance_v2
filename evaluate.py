#!/usr/bin/env python3
"""
Evaluation script for Wanderer Finance trading recommendations.

This script evaluates the performance of trading recommendations by comparing
actual stock performance against the S&P 500 benchmark.
"""

import sys
from typing import Optional
import pandas as pd
import yfinance as yf

from src.clients.sqllite import SQLiteClient
from src.utils.market_status import is_us_market_open
from src.clients.yahoo import get_sp500_percent_change
from src.config import config
from src.utils.logging_config import setup_logging, get_logger, configure_third_party_logging
from src.constants import TradingAction, EvaluationResult

# Configure logging
setup_logging(log_level="INFO", log_file="logs/evaluate.log")
configure_third_party_logging()
logger = get_logger(__name__)


def evaluate() -> bool:
    """
    Evaluate trading recommendations by comparing performance to S&P 500.

    Populates null columns (current_close, percent_change, evaluation) in the database
    using yfinance data and compares performance to S&P 500 benchmark.

    Returns:
        True if evaluation completed successfully, False otherwise
    """
    logger.info("Starting evaluation of trading recommendations")

    try:
        with SQLiteClient() as db_client:
            # Query for records that need evaluation
            query = """
            SELECT * FROM data
            WHERE current_close IS NULL OR percent_change IS NULL OR evaluation IS NULL
            ORDER BY record_date DESC, ticker ASC
            """

            df = db_client.query(query)

            if df is None or df.empty:
                logger.info("No records found requiring evaluation")
                return True

            logger.info(f"Found {len(df)} records requiring evaluation")

            # Process records in batches for better performance
            updated_records = []

            for idx, row in df.iterrows():
                try:
                    result = _evaluate_single_record(row)
                    if result:
                        updated_records.append(result)

                except Exception as e:
                    logger.error(f"Error processing record {row.get('id', 'unknown')}: {e}")
                    continue

            # Update database with results
            if updated_records:
                success = _update_database_records(db_client, updated_records)
                if success:
                    logger.info(f"Successfully updated {len(updated_records)} records")
                    return True
                else:
                    logger.error("Failed to update database records")
                    return False
            else:
                logger.warning("No records were successfully evaluated")
                return False

    except Exception as e:
        logger.error(f"Error in evaluation process: {e}", exc_info=True)
        return False


def _evaluate_single_record(row: pd.Series) -> Optional[dict]:
    """
    Evaluate a single trading record.

    Args:
        row: DataFrame row containing record data

    Returns:
        Dictionary with evaluation results or None if evaluation fails
    """
    try:
        ticker = row['ticker']
        date = row['record_date']
        id_val = row['id']
        previous_close = row['previous_close']
        action = row['action']

        logger.debug(f"Evaluating {ticker} for {date} (ID: {id_val})")

        # Validate required data
        if pd.isna(previous_close) or previous_close <= 0:
            logger.warning(f"Invalid previous_close for {ticker}: {previous_close}")
            return None

        # Get stock data
        stock = yf.Ticker(ticker)
        historical_data = stock.history(
            start=date,
            end=pd.to_datetime(date) + pd.Timedelta(days=1)
        )

        if historical_data.empty:
            logger.warning(f"No historical data found for {ticker} on {date}")
            return None

        current_close = float(historical_data['Close'].iloc[0])

        # Get S&P 500 performance
        sp500_change = get_sp500_percent_change(date)
        if sp500_change is None:
            logger.warning(f"Could not get S&P 500 data for {date}")
            return None

        # Calculate performance
        percent_change = ((current_close - previous_close) / previous_close) * 100

        # Determine evaluation result
        evaluation = _determine_evaluation(action, percent_change, sp500_change)

        return {
            'id': id_val,
            'current_close': round(current_close, 2),
            'percent_change': round(percent_change, 2),
            's&p500_percent_change': round(sp500_change, 2),
            'evaluation': evaluation
        }

    except Exception as e:
        logger.error(f"Error evaluating record: {e}")
        return None


def _determine_evaluation(action: str, stock_change: float, sp500_change: float) -> str:
    """
    Determine if a trading action was a WIN or LOSS.

    Args:
        action: Trading action (BUY/HOLD)
        stock_change: Stock percentage change
        sp500_change: S&P 500 percentage change

    Returns:
        Evaluation result (WIN/LOSS)
    """
    if action == TradingAction.BUY.value:
        return EvaluationResult.WIN.value if stock_change > sp500_change else EvaluationResult.LOSS.value
    elif action == TradingAction.HOLD.value:
        return EvaluationResult.WIN.value if stock_change < sp500_change else EvaluationResult.LOSS.value
    else:
        logger.warning(f"Unknown action '{action}', defaulting to LOSS")
        return EvaluationResult.LOSS.value


def _update_database_records(db_client: SQLiteClient, records: list) -> bool:
    """
    Update database records with evaluation results.

    Args:
        db_client: Database client instance
        records: List of evaluation results

    Returns:
        True if update successful, False otherwise
    """
    try:
        for record in records:
            query = """
            UPDATE data
            SET current_close = :current_close,
                percent_change = :percent_change,
                "s&p500_percent_change" = :sp500_percent_change,
                evaluation = :evaluation
            WHERE id = :id
            """

            success = db_client.execute_query(query, record)
            if not success:
                logger.error(f"Failed to update record {record['id']}")
                return False

        return True

    except Exception as e:
        logger.error(f"Error updating database records: {e}")
        return False



def main() -> int:
    """
    Main function to run evaluation.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        logger.info("Starting evaluation process")

        # Check if market evaluation should run
        if not config.trading.market_check_enabled or is_us_market_open():
            logger.info("Running evaluation")

            success = evaluate()
            if success:
                print("Evaluation completed successfully")
                return 0
            else:
                print("Evaluation failed. Check logs for details.")
                return 1
        else:
            logger.info("Markets are closed, skipping evaluation")
            print("Markets are closed today. Evaluation will not run.")
            return 0

    except KeyboardInterrupt:
        logger.info("Evaluation interrupted by user")
        print("\nEvaluation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)