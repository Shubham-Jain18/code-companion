import sqlite3
import json
from typing import Optional


class StateManager:
    """
    Manages the agent's state, including session and message history,
    using an SQLite database.
    """

    def __init__(self, db_path='memory.db'):
        self.db_path = db_path
        self._setup_database()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _setup_database(self):
        """Creates the necessary tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tool_used TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
            )
        """)
        conn.commit()
        conn.close()

    def create_new_session(self) -> int:
        """Creates a new session and returns its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessions DEFAULT VALUES")
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        # Add a check to ensure session_id is not None.
        if session_id is None:
            raise Exception("Failed to create a new session.")
        return session_id

    def add_message(self, session_id: int, role: str, content: str, tool_used: Optional[str] = None):
        """Adds a message to the history for a given session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, tool_used) VALUES (?, ?, ?, ?)",
            (session_id, role, str(content), tool_used)
        )
        conn.commit()
        conn.close()

    def get_session_history(self, session_id: int) -> list[dict]:
        """Retrieves the message history for a given session."""
        conn = self._get_connection()
        # This makes the cursor return rows that can be accessed by column name
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content, tool_used FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        # Convert rows to a list of dictionaries
        return [dict(row) for row in rows]
