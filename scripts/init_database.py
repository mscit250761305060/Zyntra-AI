"""Database initialization script to create all required tables."""
import logging
import sys
import mysql.connector
from mysql.connector import Error
from src.core.config import settings
from src.models.database_models import (
    USERS_TABLE_SQL,
    SESSIONS_TABLE_SQL,
    MESSAGES_TABLE_SQL,
    CONVERSATION_METADATA_TABLE_SQL,
    AGENT_INTERACTIONS_TABLE_SQL,
    AUDIT_LOG_TABLE_SQL,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("zyntra.db_init")


def create_database() -> None:
    """Create the chatbot database if it doesn't exist."""
    try:
        conn = mysql.connector.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DATABASE}")
        logger.info(f"Database '{settings.MYSQL_DATABASE}' created or already exists")
        cursor.close()
        conn.close()
    except Error as err:
        logger.error(f"Error creating database: {err}")
        raise


def create_tables() -> None:
    """Create all required tables in the database."""
    tables = [
        ("users", USERS_TABLE_SQL),
        ("sessions", SESSIONS_TABLE_SQL),
        ("messages", MESSAGES_TABLE_SQL),
        ("conversation_metadata", CONVERSATION_METADATA_TABLE_SQL),
        ("agent_interactions", AGENT_INTERACTIONS_TABLE_SQL),
        ("audit_logs", AUDIT_LOG_TABLE_SQL),
    ]

    try:
        conn = mysql.connector.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
        )
        cursor = conn.cursor()

        for table_name, sql in tables:
            try:
                cursor.execute(sql)
                logger.info(f"Table '{table_name}' created or already exists")
            except Error as err:
                logger.error(f"Error creating table '{table_name}': {err}")
                raise

        cursor.close()
        conn.close()
        logger.info("All tables created successfully")

    except Error as err:
        logger.error(f"Error connecting to database: {err}")
        raise


def main() -> None:
    """Main function to initialize the database."""
    logger.info("Starting database initialization...")
    logger.info(
        f"MySQL Configuration: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
    )

    try:
        create_database()
        create_tables()
        logger.info("Database initialization completed successfully")
    except Exception as err:
        logger.error(f"Database initialization failed: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
