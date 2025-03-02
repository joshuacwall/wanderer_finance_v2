import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData, Table, Index
import logging

class SQLiteClient:
    def __init__(self, db_path="main.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), db_path))
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        self.metadata = MetaData()
        self.logger.info(f"SQLiteClient initialized with database: {self.db_path}")

    def query(self, query):
        try:
            self.logger.info(f"Executing query: {query}")
            df = pd.read_sql_query(query, self.engine)
            self.logger.info("Query executed successfully.")
            return df
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            return None

    def execute_query(self, query, params=None):
        try:
            self.logger.info(f"Executing query: {query}")
            with self.engine.connect() as connection:
                print(f"Executing SQL: {query}") #print statement added.
                if params:
                    connection.execute(query, (params,))
                else:
                    connection.execute(query)
                connection.commit()
            self.logger.info("Query executed successfully.")
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")

    def close(self):
        self.engine.dispose()
        self.logger.info("SQLite connection closed.")

    def append_df(self, df, table_name):
        try:
            self.logger.info(f"Appending DataFrame to {table_name}")
            df.to_sql(table_name, self.engine, if_exists='append', index=False)
            self.logger.info(f"DataFrame appended to {table_name} successfully.")
        except Exception as e:
            self.logger.error(f"Error appending DataFrame: {e}")

    def create_table(self, table_name, columns):
        try:
            table_columns = [Column(name, col_type) for name, col_type in columns.items()]
            table = Table(table_name, self.metadata, *table_columns)
            self.metadata.create_all(self.engine)
            self.logger.info(f"Table {table_name} created successfully.")
            self.add_indexes(table_name, list(columns.keys()))

        except Exception as e:
            self.logger.error(f"Error creating table {table_name}: {e}")

    def add_indexes(self, table_name, columns):
        for col in columns:
            index_name = f"idx_{table_name}_{col}"
            try:
                Index(index_name, Table(table_name, self.metadata, autoload_with=self.engine), Column(col)).create(self.engine)
                self.logger.info(f"Index {index_name} created successfully.")
            except Exception as e:
                self.logger.error(f"Error creating index {index_name}: {e}")