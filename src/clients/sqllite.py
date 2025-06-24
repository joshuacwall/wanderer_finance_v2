"""
SQLite database client for Wanderer Finance application.

This module provides a robust SQLite client with proper error handling,
logging, and connection management.
"""

import os
from typing import Optional, Dict, Any, List, Union
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData, Table, Index, text
from sqlalchemy.exc import SQLAlchemyError

from src.utils.logging_config import get_logger
from src.config import config

logger = get_logger(__name__)


class SQLiteClient:
    """
    SQLite database client with connection management and error handling.

    This client provides methods for querying, inserting, and managing
    SQLite database operations with proper logging and error handling.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize SQLite client.

        Args:
            db_path: Path to SQLite database file. Uses config default if None.
        """
        self.db_path = db_path or config.database.absolute_path

        try:
            self.engine = create_engine(
                f'sqlite:///{self.db_path}',
                pool_pre_ping=True,
                pool_recycle=3600
            )
            self.metadata = MetaData()
            logger.info(f"SQLiteClient initialized with database: {self.db_path}")

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

        except Exception as e:
            logger.error(f"Failed to initialize SQLite client: {e}")
            raise

    def query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[pd.DataFrame]:
        """
        Execute a SELECT query and return results as DataFrame.

        Args:
            query: SQL query string
            params: Optional parameters for parameterized queries

        Returns:
            DataFrame with query results or None if query fails
        """
        try:
            logger.debug(f"Executing query: {query[:100]}...")

            with self.engine.connect() as conn:
                df = pd.read_sql_query(query, conn, params=params)

            logger.info(f"Query executed successfully, returned {len(df)} rows")
            return df

        except SQLAlchemyError as e:
            logger.error(f"Database error executing query: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            return None

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Execute a non-SELECT query (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query string
            params: Optional parameters for parameterized queries

        Returns:
            True if query executed successfully, False otherwise
        """
        try:
            logger.debug(f"Executing non-select query: {query[:100]}...")

            with self.engine.connect() as connection:
                if params:
                    connection.execute(text(query), params)
                else:
                    connection.execute(text(query))
                connection.commit()

            logger.info("Non-select query executed successfully")
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error executing query: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            return False

    def close(self) -> None:
        """Close database connection and dispose of engine."""
        try:
            self.engine.dispose()
            logger.info("SQLite connection closed")
        except Exception as e:
            logger.error(f"Error closing SQLite connection: {e}")

    def append_df(self, df: pd.DataFrame, table_name: str) -> bool:
        """
        Append DataFrame to database table.

        Args:
            df: DataFrame to append
            table_name: Name of target table

        Returns:
            True if successful, False otherwise
        """
        try:
            if df.empty:
                logger.warning(f"Attempted to append empty DataFrame to {table_name}")
                return False

            logger.info(f"Appending {len(df)} rows to {table_name}")
            df.to_sql(table_name, self.engine, if_exists='append', index=False)
            logger.info(f"DataFrame appended to {table_name} successfully")
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error appending DataFrame to {table_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error appending DataFrame to {table_name}: {e}")
            return False

    def create_table(self, table_name: str, columns: Dict[str, Any]) -> bool:
        """
        Create database table with specified columns.

        Args:
            table_name: Name of table to create
            columns: Dictionary mapping column names to SQLAlchemy column types

        Returns:
            True if successful, False otherwise
        """
        try:
            table_columns = [Column(name, col_type) for name, col_type in columns.items()]
            table = Table(table_name, self.metadata, *table_columns)
            self.metadata.create_all(self.engine)
            logger.info(f"Table {table_name} created successfully")

            # Add indexes for better performance
            self._add_indexes(table_name, list(columns.keys()))
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error creating table {table_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating table {table_name}: {e}")
            return False

    def _add_indexes(self, table_name: str, columns: List[str]) -> None:
        """
        Add indexes to table columns for better query performance.

        Args:
            table_name: Name of table
            columns: List of column names to index
        """
        for col in columns:
            if col in ['id', 'ticker', 'record_date']:  # Only index important columns
                index_name = f"idx_{table_name}_{col}"
                try:
                    table = Table(table_name, self.metadata, autoload_with=self.engine)
                    Index(index_name, table.c[col]).create(self.engine, checkfirst=True)
                    logger.debug(f"Index {index_name} created successfully")
                except Exception as e:
                    logger.warning(f"Could not create index {index_name}: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()