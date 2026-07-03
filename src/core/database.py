import logging
import mysql.connector
from mysql.connector import pooling, Error
from typing import Optional, Dict, Any, List
from src.core.config import settings
from contextlib import contextmanager

logger = logging.getLogger("zyntra.database")


class DatabaseManager:
    """Manages MySQL database connections and provides query execution methods."""

    def __init__(self):
        self.pool: Optional[pooling.MySQLConnectionPool] = None
        self._initialized = False

    def _ensure_pool(self) -> None:
        """Initialize the pool on first use (lazy initialization)."""
        if self._initialized:
            return
        
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name=settings.MYSQL_POOL_NAME,
                pool_size=settings.MYSQL_POOL_SIZE,
                pool_reset_session=settings.MYSQL_POOL_RESET_SESSION,
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DATABASE,
                autocommit=True,
            )
            self._initialized = True
            logger.info(
                f"MySQL connection pool initialized: {settings.MYSQL_HOST}:"
                f"{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
            )
        except Error as err:
            logger.error(f"Error initializing MySQL connection pool: {err}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager to get a connection from the pool."""
        conn = None
        try:
            self._ensure_pool()
            if not self.pool:
                raise Exception("Connection pool not initialized")
            conn = self.pool.get_connection()
            yield conn
        except Error as err:
            logger.error(f"Error getting connection from pool: {err}")
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params)
                results = cursor.fetchall()
                cursor.close()
                return results
        except Error as err:
            logger.error(f"Query execution error: {err}")
            raise

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last inserted ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                last_id = cursor.lastrowid
                cursor.close()
                return last_id
        except Error as err:
            logger.error(f"Insert execution error: {err}")
            raise

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an UPDATE query and return the number of affected rows."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows
        except Error as err:
            logger.error(f"Update execution error: {err}")
            raise

    def execute_delete(self, query: str, params: tuple = ()) -> int:
        """Execute a DELETE query and return the number of affected rows."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows
        except Error as err:
            logger.error(f"Delete execution error: {err}")
            raise

    def close_pool(self) -> None:
        """Close all connections in the pool."""
        try:
            if self.pool:
                # Note: mysql-connector-python doesn't have a direct pool close method
                # Connections are closed individually
                logger.info("Connection pool closed")
        except Error as err:
            logger.error(f"Error closing connection pool: {err}")


    def init_db(self) -> None:
        """Initialize database tables."""
        from src.models.database_models import (
            USERS_TABLE_SQL,
            SESSIONS_TABLE_SQL,
            MESSAGES_TABLE_SQL,
            CONVERSATION_METADATA_TABLE_SQL,
            AGENT_INTERACTIONS_TABLE_SQL,
            AUDIT_LOG_TABLE_SQL,
            REFRESH_TOKENS_TABLE_SQL
        )
        try:
            self._ensure_pool()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for query in [
                    USERS_TABLE_SQL,
                    SESSIONS_TABLE_SQL,
                    MESSAGES_TABLE_SQL,
                    CONVERSATION_METADATA_TABLE_SQL,
                    AGENT_INTERACTIONS_TABLE_SQL,
                    AUDIT_LOG_TABLE_SQL,
                    REFRESH_TOKENS_TABLE_SQL
                ]:
                    cursor.execute(query)
                conn.commit()
                cursor.close()
            logger.info("Database tables initialized successfully")
        except Error as err:
            logger.error(f"Error initializing database tables: {err}")
            raise

# Global database manager instance
db_manager = DatabaseManager()
