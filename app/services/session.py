import sqlite3
from datetime import datetime
import json
from typing import List, Dict, Any

DB_PATH = "data/sessions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (session_id TEXT PRIMARY KEY, user_id TEXT, created_at TEXT, updated_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

class SessionService:
    def __init__(self):
        init_db()

    def create_session(self, session_id: str, user_id: str):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute("INSERT OR IGNORE INTO sessions (session_id, user_id, created_at, updated_at) VALUES (?, ?, ?, ?)",
                  (session_id, user_id, now, now))
        conn.commit()
        conn.close()

    def add_message(self, session_id: str, role: str, content: str):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute("INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                  (session_id, role, content, now))
        c.execute("UPDATE sessions SET updated_at = ? WHERE session_id = ?", (now, session_id))
        conn.commit()
        conn.close()

    def get_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                  (session_id, limit))
        rows = c.fetchall()
        conn.close()
        return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in reversed(rows)]
