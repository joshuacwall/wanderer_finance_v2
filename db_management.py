import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData, Table
import logging
from dotenv import load_dotenv

load_dotenv()

DATABASE = "analysis_results.db"

def setup_database(db_path, table_schemas):
    """
    Sets up the database and creates multiple tables with specified schemas, only if they don't exist.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), db_path))
        engine = create_engine(f'sqlite:///{db_path}')
        metadata = MetaData()

        for table_name, columns in table_schemas.items():
            if not engine.dialect.has_table(engine, table_name): #Check if table exists.
                table_columns = [Column(name, col_type) for name, col_type in columns.items()]
                Table(table_name, metadata, *table_columns)  # create table object.
                metadata.create_all(engine)  # create the tables.
                logger.info(f"Table '{table_name}' created successfully.")
            else:
                logger.info(f"Table '{table_name}' already exists, skipping creation.")

        logger.info("Database setup complete.")

    except Exception as e:
        logger.error(f"Error setting up database: {e}")

if __name__ == "__main__":
    table_schemas = {
        "raw_data": {
            'ticker': String,
            'action': String,
            'explanation': String,
            'current_date': Date,
            'article_links_and_sentiments': String,
            "previous_close": Float,
            "current_close": Float,
            "percent_change": Float,
            "evaluation": String,
        },
        # Add other table schemas if needed
    }

    setup_database(DATABASE, table_schemas)
    print("Database table creation/check completed.")