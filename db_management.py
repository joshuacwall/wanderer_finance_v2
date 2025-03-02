import os
from sqlalchemy import create_engine, Column, String, Float, Date, MetaData, Table, Integer, inspect
import logging
from dotenv import load_dotenv

load_dotenv()

DATABASE = "main.db"

def create_table(engine, metadata, table_name, columns):
    """Creates a table if it doesn't exist."""
    if not inspect(engine).has_table(table_name):
        table = Table(table_name, metadata, *columns)
        metadata.create_all(engine)
        logging.info(f"Table '{table_name}' created successfully.")
    else:
        logging.info(f"Table '{table_name}' already exists, skipping creation.")

def setup_database(db_path, table_schemas):
    """Sets up the database and creates multiple tables with specified schemas."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    try:
        db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)) #More robust path handling.
        engine = create_engine(f'sqlite:///{db_path}')
        metadata = MetaData()

        for table_name, columns_dict in table_schemas.items():
            columns = [col for col in columns_dict.values()] #get a list of column objects.
            create_table(engine, metadata, table_name, columns)

        logger.info("Database setup complete.")

    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise #Reraise to stop execution and see the error.

if __name__ == "__main__":
    table_schemas = {
        "data": {
            'id': Column('id', Integer, primary_key=True, autoincrement=True),
            'ticker': Column('ticker', String),
            'action': Column('action', String),
            'explanation': Column('explanation', String),
            'current_date': Column('current_date', Date),
            'article_links_and_sentiments': Column('article_links_and_sentiments', String),
            "previous_close": Column("previous_close", Float),
            "current_close": Column("current_close", Float),
            "percent_change": Column("percent_change", Float),
            "s&p500_percent_change": Column("s&p500_percent_change", Float),
            "evaluation": Column("evaluation", String),
        },
        # Add other table schemas if needed
    }

    try:
        setup_database(DATABASE, table_schemas)
        print("Database table creation/check completed.")
    except Exception as e:
        print(f"An error occurred: {e}")