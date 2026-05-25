import sqlite3
from pathlib import Path
from typing import Dict, List


class ChatHistoryStore:
    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_turn(self, session_id: str, user_message: str, assistant_message: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO chat_history (session_id, user_message, assistant_message) VALUES (?, ?, ?)",
                (session_id, user_message, assistant_message),
            )
            conn.commit()

    def get_recent(self, session_id: str, limit: int = 5) -> List[Dict[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT user_message, assistant_message FROM chat_history WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        rows = list(reversed(rows))
        return [{"user": r[0], "assistant": r[1]} for r in rows]
