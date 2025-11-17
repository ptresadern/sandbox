"""Database models and operations for users and conversations"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager


class Database:
    """SQLite database handler for users and conversations"""

    def __init__(self, db_path: str = "./data/app.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    is_admin BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Conversations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """
            )

            # Messages table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sources TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """
            )

    # User operations
    def create_user(self, username: str, hashed_password: str, is_admin: bool = False) -> int:
        """Create a new user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, hashed_password, is_admin) VALUES (?, ?, ?)",
                (username, hashed_password, is_admin),
            )
            return cursor.lastrowid

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # Conversation operations
    def create_conversation(self, user_id: int, title: str = "New Conversation") -> int:
        """Create a new conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (user_id, title) VALUES (?, ?)",
                (user_id, title),
            )
            return cursor.lastrowid

    def get_conversations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all conversations for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM conversations
                WHERE user_id = ?
                ORDER BY updated_at DESC
            """,
                (user_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_conversation(self, conversation_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations WHERE id = ? AND user_id = ?",
                (conversation_id, user_id),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_conversation_timestamp(self, conversation_id: int):
        """Update the last modified timestamp of a conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,),
            )

    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation and its messages"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Verify ownership
            cursor.execute(
                "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
                (conversation_id, user_id),
            )
            if not cursor.fetchone():
                return False

            # Delete messages first
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            # Delete conversation
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            return True

    # Message operations
    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        sources: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        """Add a message to a conversation"""
        sources_json = json.dumps(sources) if sources else None
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, sources) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, sources_json),
            )
            # Update conversation timestamp
            cursor.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,),
            )
            return cursor.lastrowid

    def get_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
        """Get all messages in a conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            """,
                (conversation_id,),
            )
            messages = []
            for row in cursor.fetchall():
                msg = dict(row)
                if msg["sources"]:
                    msg["sources"] = json.loads(msg["sources"])
                messages.append(msg)
            return messages

    def get_conversation_with_messages(
        self, conversation_id: int, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get conversation with all its messages"""
        conversation = self.get_conversation(conversation_id, user_id)
        if conversation:
            conversation["messages"] = self.get_messages(conversation_id)
        return conversation


# Global database instance
db = Database()
