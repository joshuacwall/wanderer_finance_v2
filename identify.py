#!/usr/bin/env python3
"""
Stock identification and analysis script for Wanderer Finance.

This script identifies and analyzes the most active stocks during market hours,
storing the results in the database for later evaluation and display.
"""

import sys
from typing import Optional

from src.utils.market_status import is_us_market_open
from src.clients.sqllite import SQLiteClient
from src.workflows.analyze_active_stocks import analyze_active_stocks
from src.config import config
from src.utils.logging_config import setup_logging, get_logger, configure_third_party_logging
from src.constants import MarketStatus

# Configure logging
setup_logging(log_level="INFO", log_file="logs/identify.log")
configure_third_party_logging()
logger = get_logger(__name__)


def main(max_stocks: Optional[int] = None) -> int:
    """
    Main function to identify and analyze active stocks.

    Args:
        max_stocks: Maximum number of stocks to analyze (None for all)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        logger.info("Starting stock identification and analysis")

        # Check if market is open
        if not config.trading.market_check_enabled or is_us_market_open():
            logger.info("Market is open, proceeding with analysis")

            # Analyze active stocks
            results_df = analyze_active_stocks(
                model=config.llm.model,
                temperature=config.llm.temperature,
                max_stocks=max_stocks
            )

            if not results_df.empty:
                # Store results in database
                with SQLiteClient() as client:
                    success = client.append_df(results_df, config.database.table_name)

                if success:
                    logger.info("Analysis completed successfully")
                    print("\n" + "="*50)
                    print("ANALYSIS SUMMARY")
                    print("="*50)
                    print(f"Total stocks analyzed: {len(results_df)}")
                    print(f"Database: {config.database.absolute_path}")
                    print(f"Table: {config.database.table_name}")
                    print("\nAction Distribution:")
                    action_counts = results_df['action'].value_counts()
                    for action, count in action_counts.items():
                        print(f"  {action}: {count}")
                    print("="*50)
                    return 0
                else:
                    logger.error("Failed to store results in database")
                    return 1
            else:
                logger.warning("No stocks were analyzed successfully")
                print("No stocks were analyzed. Check logs for details.")
                return 1
        else:
            logger.info("Markets are closed today")
            print("Markets are closed today. Analysis will not run.")
            return 0

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        print("\nAnalysis interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    # Parse command line arguments for max_stocks if needed
    max_stocks_arg = None
    if len(sys.argv) > 1:
        try:
            max_stocks_arg = int(sys.argv[1])
            logger.info(f"Limiting analysis to {max_stocks_arg} stocks")
        except ValueError:
            logger.warning(f"Invalid max_stocks argument: {sys.argv[1]}")

    exit_code = main(max_stocks=max_stocks_arg)
    sys.exit(exit_code)


