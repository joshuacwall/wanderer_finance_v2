import pandas as pd
import logging
import yfinance as yf
from src.clients.sqllite import SQLiteClient
from src.utils.market_status import is_us_market_open
from src.clients.yahoo import get_sp500_percent_change

def evaluate():
    """
    Populates null columns (current_close, percent_change, evaluation) in evaluated_data using yfinance and pandas,
    comparing to S&P 500 performance.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    db_client = SQLiteClient()

    try:
        query = """
        SELECT * FROM data 
        WHERE current_close IS NULL OR percent_change IS NULL OR evaluation IS NULL
        """

        df = db_client.query(query)

        if df is None or df.empty:
            logger.info("No records found with null columns.")
            return

        for idx, row in df.iterrows():
            try:
                ticker: str = row['ticker']
                date: str = row['current_date']
                id_val: int = row['id']
                previous_close: float = row['previous_close']
                action: str = row['action']

                logger.info(f"Processing data for ticker: {ticker}, date: {date}, id: {id_val}")

                try:
                    stock = yf.Ticker(ticker)
                    historical_data = stock.history(start=date, end=pd.to_datetime(date) + pd.Timedelta(days=1))

                    sp500 = get_sp500_percent_change(date)

                    current_close: float = historical_data['Close'].iloc[0]
                    percent_change: float = ((current_close - previous_close) / previous_close) * 100

                    evaluation: str | None = None
                    if action == 'BUY':
                        evaluation = 'WIN' if percent_change > sp500 else 'LOSS'
                    elif action == 'HOLD':
                        evaluation = 'WIN' if percent_change < sp500 else 'LOSS'

                    # Update the DataFrame directly
                    df.loc[idx, 'current_close'] = round(current_close, 2)
                    df.loc[idx, 'percent_change'] = round(percent_change, 2)
                    df.loc[idx, 's&p500_percent_change'] = round(sp500, 2)
                    df.loc[idx, 'evaluation'] = evaluation

                    logger.info(f"Updated data for {ticker}, date: {date}, id: {id_val}")

                except Exception as yf_error:
                    logger.warning(f"yfinance error for {ticker} or S&P 500, date: {date}: {yf_error}")

            except Exception as e:
                logger.error(f"Error processing {ticker}, date: {date}, id: {id_val}: {e}")
                continue

        # Write the updated DataFrame back to the database
        if not df.empty:
            df.to_sql('data', db_client.engine, if_exists='replace', index=False)
            logger.info("DataFrame updated in the database.")

    except Exception as e:
        logger.error(f"Error in populate_null_columns: {e}")

    finally:
        db_client.close()

if __name__ == "__main__":
    if is_us_market_open():
        evaluate()
    else:
        print("Markets are closed today")