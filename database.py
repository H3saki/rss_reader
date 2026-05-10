import sqlite3
import shutil
import os
from datetime import datetime
from rss_reader.logger import logger
from rss_reader.config_loader import db_path, backup_folder

# List of allowed table names to prevent SQL injection risks when using f-strings for table identifiers.
ALLOWED_TABLES = ["cyber_news", "finnish_news", "favorites"]

def validate_table_name(table_name):
    """
    Ensures the given table name is one of the allowed table names.
    Raises a ValueError if an invalid table name is used to prevent SQL injection.
    """
    if table_name not in ALLOWED_TABLES:
        logger.error(f"Attempt to access invalid table: {table_name}")
        raise ValueError(f"Invalid table name: {table_name}")

def connect_db():
    """
    Establishes and returns a connection to the SQLite database.
    Logs and raises an error if the connection fails.
    """
    try:
        return sqlite3.connect(db_path)
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

# ⚠️ Security Note:
# You can't parameterize SQL identifiers (like table names or column names) using ? placeholders.
# This function uses f-strings for trusted table names validated by validate_table_name().
def create_table(conn, table_name):
    """
    Creates the specified articles table and a common 'favorites' table if they don't already exist.
    """
    validate_table_name(table_name)

    # Create main articles table for the given table name
    conn.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            published TEXT,
            category TEXT,
            title TEXT,
            content TEXT,
            source TEXT,
            tags TEXT,
            link TEXT UNIQUE
        )
    ''')

    # Create a table for favorited articles (only one 'favorites' table shared by all sources)
    conn.execute(f'''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY,
            published TEXT,
            title TEXT,
            content TEXT,
            source TEXT,
            keyword TEXT,
            link TEXT UNIQUE
        )
    ''')

    conn.commit()

def insert_article(conn, title, link, published, content, category, source, tags_str, table_name):
    """
    Inserts an article into the specified table.
    Skips duplicate entries (based on the unique link field).
    Logs any other exceptions that occur.
    """
    validate_table_name(table_name)
    try:
        conn.execute(
            f"INSERT INTO {table_name} (title, link, published, content, category, source, tags) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, link, published, content, category, source, tags_str)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # Log duplicate articles (same link) and skip insertion.
        logger.debug(f"Duplicate article found for link: {link}. Skipping insertion.")
    except Exception as e:
        logger.error(f"Failed to insert article: {e}")

def backup_database(original_path=db_path, backup=backup_folder):
    """
    Creates a timestamped backup copy of the database file inside the specified backup folder.
    Creates the backup directory if it doesn't already exist.
    """
    os.makedirs(backup, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup, f"db_backup_{timestamp}.db")
    shutil.copy2(original_path, backup_path)
    print(f"Backup created: {backup_path}")

# If this file is executed directly, create a backup of the database.
if __name__ == '__main__':
    backup_database()