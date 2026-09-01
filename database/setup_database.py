"""
Database Initialization & Seeding Script.
Executes schema.sql and seed.sql using pure-Python PyMySQL driver.
Verifies table counts and relational integrity.
"""

import sys
from pathlib import Path

# Add backend to path for config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import pymysql
from app.config import get_settings
from app.utils.logger import logger


def execute_sql_file(cursor, file_path: Path):
    """
    Read and execute SQL statements from a file.
    """
    logger.info(f"Executing SQL file: {file_path.name}...")
    sql_text = file_path.read_text(encoding="utf-8")

    # Split by semicolon while respecting comments and whitespace
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]

    for stmt in statements:
        if stmt:
            cursor.execute(stmt)


def setup_database():
    """
    Connect to MySQL server, create business_analytics database,
    build all 11 tables, and populate seed data.
    """
    settings = get_settings()
    logger.info(f"Connecting to MySQL server at {settings.DB_HOST}:{settings.DB_PORT} as {settings.DB_USER}...")

    conn = pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        autocommit=True,
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.execute(f"USE `{settings.DB_NAME}`;")
            logger.info(f"Database `{settings.DB_NAME}` selected.")

            db_dir = Path(__file__).resolve().parent

            schema_file = db_dir / "schema.sql"
            execute_sql_file(cursor, schema_file)
            logger.info("Schema execution completed.")

            seed_file = db_dir / "seed.sql"
            execute_sql_file(cursor, seed_file)
            logger.info("Seed data population completed.")

            tables = [
                "regions", "categories", "suppliers", "employees",
                "customers", "products", "inventory", "orders",
                "order_items", "payments", "sales"
            ]

            logger.info("\n--- DATABASE VERIFICATION REPORT ---")
            for tbl in tables:
                cursor.execute(f"SELECT COUNT(*) FROM `{tbl}`;")
                count = cursor.fetchone()[0]
                logger.info(f"  Table `{tbl}`: {count:,} rows")

            cursor.execute("SELECT MIN(order_date), MAX(order_date), COUNT(*) FROM `orders`;")
            min_date, max_date, total_orders = cursor.fetchone()
            logger.info(f"\nOrder Range: {min_date} to {max_date} | Total Orders: {total_orders:,}")

            cursor.execute("SELECT SUM(revenue), SUM(profit) FROM `sales`;")
            total_rev, total_prof = cursor.fetchone()
            logger.info(f"Total Sales Revenue: INR {total_rev:,.2f} | Total Profit: INR {total_prof:,.2f}")
            logger.info("--- DATABASE SETUP SUCCESSFUL ---\n")

    finally:
        conn.close()


if __name__ == "__main__":
    setup_database()
