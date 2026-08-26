"""Conversation history store for AIPet messages."""

import datetime
from typing import List, Dict, Any, Optional
from app.memory.database import get_db, Database
from app.core.logger import logger
from app.core.exceptions import DatabaseError

class ConversationStore:
    """Provides methods to insert, fetch, and clear persistent conversation messages."""

    def __init__(self, db: Optional[Database] = None, session_id: str = "default_session"):
        self.db = db if db is not None else get_db()
        self.session_id = session_id

    def add_message(self, role: str, content: str, image_path: Optional[str] = None) -> int:
        """Add a message to the conversation history."""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.datetime.now(datetime.timezone.utc).isoformat()
                cursor.execute("""
                    INSERT INTO messages (session_id, role, content, image_path, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.session_id, role, content, image_path, now))
                conn.commit()
                msg_id = cursor.lastrowid
                logger.debug(f"Stored message [{role}]: {content[:30]}...")
                return msg_id
        except Exception as e:
            logger.error(f"Failed to store conversation message: {e}")
            raise DatabaseError(f"Failed to save message: {e}")

    def get_recent_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent conversation messages ordered chronologically."""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, role, content, image_path, timestamp
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                """, (self.session_id, limit))
                rows = cursor.fetchall()
                messages = [dict(row) for row in reversed(rows)]
                return messages
        except Exception as e:
            logger.error(f"Failed to fetch conversation history: {e}")
            return []

    def clear_history(self) -> bool:
        """Clear all conversation history for the current session."""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE session_id = ?", (self.session_id,))
                conn.commit()
                logger.info(f"Cleared conversation history for session {self.session_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to clear conversation history: {e}")
            return False
