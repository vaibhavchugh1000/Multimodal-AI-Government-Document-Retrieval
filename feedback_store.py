
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path

# Store the database beside this Python file.
DB_PATH = Path(__file__).resolve().parent / "feedback.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_feedback_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                retrieved_sources TEXT,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_id INTEGER NOT NULL UNIQUE,
                rating INTEGER NOT NULL CHECK (rating IN (-1, 1)),
                comment TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (interaction_id)
                    REFERENCES interactions(id)
            )
        """)


def save_interaction(question, answer, sources):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO interactions
                (question, answer, retrieved_sources, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            question,
            answer,
            json.dumps(sources, ensure_ascii=False, default=str),
            datetime.now(timezone.utc).isoformat()
        ))

        return cursor.lastrowid


def save_feedback(interaction_id, rating):
    """Save or update the rating without overwriting the comment."""
    if isinstance(rating, bool) or rating not in (1, -1):
        raise ValueError("Rating must be 1 or -1")

    with get_connection() as conn:
        existing = conn.execute("""
            SELECT id FROM feedback WHERE interaction_id = ?
        """, (interaction_id,)).fetchone()

        now = datetime.now(timezone.utc).isoformat()

        if existing:
            conn.execute("""
                UPDATE feedback
                SET rating = ?, created_at = ?
                WHERE interaction_id = ?
            """, (rating, now, interaction_id))
        else:
            conn.execute("""
                INSERT INTO feedback
                    (interaction_id, rating, comment, created_at)
                VALUES (?, ?, NULL, ?)
            """, (interaction_id, rating, now))


def save_feedback_comment(interaction_id, comment):
    """Save the comment independently for an existing rating."""
    if not isinstance(comment, str):
        raise ValueError("Comment must be text")

    comment = comment.strip()[:1000]

    if not comment:
        raise ValueError("Comment cannot be empty")

    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE feedback
            SET comment = ?
            WHERE interaction_id = ?
        """, (comment, interaction_id))

        if cursor.rowcount == 0:
            raise ValueError(
                "Save a Helpful or Not helpful rating before saving a comment."
            )
