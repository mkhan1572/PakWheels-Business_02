"""
config.py — MySQL connection helper for pakwheels_db.
Reads credentials from the .env file in the backend/ directory.
"""
import os
import MySQLdb
from dotenv import load_dotenv

# Load .env from the same folder as this file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DB_CONFIG = {
    "host":        os.getenv("DB_HOST", "localhost"),
    "user":        os.getenv("DB_USER", "root"),
    "passwd":      os.getenv("DB_PASS", ""),
    "db":          os.getenv("DB_NAME", "pakwheels_db"),
    "charset":     "utf8mb4",
    "use_unicode": True,
}


def get_db():
    """Return a live MySQLdb connection to pakwheels_db."""
    try:
        return MySQLdb.connect(**DB_CONFIG)
    except MySQLdb.OperationalError as e:
        raise RuntimeError(
            f"Cannot connect to MySQL at {DB_CONFIG['host']} "
            f"(db={DB_CONFIG['db']}): {e}"
        ) from e
