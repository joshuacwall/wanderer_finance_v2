from src.clients.yahoo import get_current_day_metrics
import pandas as pd
import logging
from src.utils.market_status import is_us_market_open
from src.clients.sqllite import SQLiteClient

def update_with_evaluation():
    """
    Updates all stock analysis results in SQLite database that have missing end-of-day data,
    regardless of date. Uses the date stored in the database for each record.
    """
    # Initialize logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize SQLite client
    db_client = SQLiteClient()
    
    try:
        # Query for all records that haven't been evaluated yet
        query = """
        SELECT id, ticker, action, previous_close, current_date 
        FROM raw_data 
        WHERE (current_close IS NULL 
            OR percent_change IS NULL 
            OR evaluation IS NULL)
        """
        
        # Execute query using pandas
        df = db_client.query(query)
        
        if df is None or df.empty:
            logger.info("No records found for updating")
            return
        
        # Process each record
        for idx, row in df.iterrows():
            try:
                ticker = row['ticker']
                date = row['current_date']
                logger.info(f"Processing data for ticker: {ticker} from date: {date}")
                
                # Get current day's closing data
                stock_data = get_current_day_metrics(ticker, date=date)
                
                if stock_data is not None and 'Close' in stock_data:
                    current_close = stock_data['Close']
                    previous_close = float(row['previous_close'])
                    
                    # Calculate percent change
                    percent_change = ((current_close - previous_close) / previous_close) * 100
                    
                    # Determine evaluation
                    evaluation = None
                    if row['action'] == 'BUY':
                        evaluation = 'WIN' if percent_change > 0 else 'LOSE'
                    
                    # Update the database record
                    update_query = """
                    UPDATE analysis_results 
                    SET 
                        current_close = ?,
                        percent_change = ?,
                        evaluation = ?
                    WHERE id = ?
                    """
                    
                    db_client.execute_query(
                        update_query, 
                        params=(
                            round(current_close, 2),
                            round(percent_change, 2),
                            evaluation,
                            row['id']
                        )
                    )
                    
                    logger.info(f"Updated data for {ticker} from {date}")
                else:
                    logger.warning(f"Could not retrieve closing data for {ticker} from {date}")
                    
            except Exception as e:
                logger.error(f"Error processing data for {ticker} from {date}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error in update_missing_analysis: {e}")
    
    finally:
        # Close database connection
        db_client.close()


if __name__ == "__main__":
    if is_us_market_open():
        update_with_evaluation()

    else:
        print("Markets are closed today")
