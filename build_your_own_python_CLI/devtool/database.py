import sqlite3
import os

# Create a hidden folder in the user's home directory (e.g., C:\Users\Name\.devtool)
APP_DIR = os.path.join(os.path.expanduser("~"), ".devtool")
DB_PATH = os.path.join(APP_DIR, "devtool.db")

def get_connection():
    """Creates and returns a connection to the SQLite database."""
    # Ensure the directory exists before connecting
    os.makedirs(APP_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    # This allows us to access columns by name (e.g., row["title"])
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    """Creates the necessary tables if they don't exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()