"""
Database initialization and management
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

# Database path
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "agentic_chat.db"

def init_database():
    """Initialize database with schema"""
    # Ensure data directory exists
    DB_DIR.mkdir(exist_ok=True)
    
    # Read schema
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    # Execute schema
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema)
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at {DB_PATH}")

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Get database connection context manager"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_query(query: str, params: tuple = ()):
    """Execute a query and return results"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def execute_update(query: str, params: tuple = ()):
    """Execute an update/insert/delete query"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.rowcount

# Initialize database on import
if not DB_PATH.exists():
    init_database()
