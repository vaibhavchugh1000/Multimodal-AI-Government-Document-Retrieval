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
    """Create the three tables for interaction and feedback storage."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                retrieval_top_k INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS interaction_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_id INTEGER NOT NULL,
                chunk_id TEXT NOT NULL,
                chunk_rank INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                distance REAL,
                metadata TEXT,
                is_cited INTEGER NOT NULL DEFAULT 0
                    CHECK (is_cited IN (0, 1)),

                FOREIGN KEY (interaction_id)
                    REFERENCES interactions(id)
                    ON DELETE CASCADE,

                UNIQUE (interaction_id, chunk_rank)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_id INTEGER NOT NULL UNIQUE,
                is_helpful INTEGER NOT NULL
                    CHECK (is_helpful IN (0, 1)),
                comment TEXT,
                created_at TEXT NOT NULL,

                FOREIGN KEY (interaction_id)
                    REFERENCES interactions(id)
                    ON DELETE CASCADE
            )
        """)


def save_interaction(question, answer, retrieved_chunks, retrieval_top_k):
    """
    Save one interaction and all chunks retrieved for it.

    Each item in retrieved_chunks must contain:
      - chunk_id: persistent ChromaDB chunk ID
      - text: original retrieved chunk text
      - distance: ChromaDB distance value (or None)
      - metadata: metadata dictionary (optional)
      - is_cited: True if its source is shown to the user, otherwise False

    chunk_rank is assigned from the order of retrieved_chunks (starting at 1).
    Returns the newly created interaction ID.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not isinstance(retrieval_top_k, int) or retrieval_top_k < 1:
        raise ValueError("retrieval_top_k must be a positive integer.")

    if not isinstance(retrieved_chunks, (list, tuple)):
        raise ValueError("retrieved_chunks must be a list or tuple.")

    # Keep the complete structured answer as JSON when a Python object is supplied.
    if isinstance(answer, (dict, list)):
        answer_to_store = json.dumps(
            answer, ensure_ascii=False, default=str
        )
    elif isinstance(answer, str):
        answer_to_store = answer
    else:
        raise ValueError("Answer must be a string, dictionary, or list.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO interactions
                (question, answer, retrieval_top_k, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            question.strip(),
            answer_to_store,
            retrieval_top_k,
            now
        ))

        interaction_id = cursor.lastrowid

        chunk_rows = []

        for rank, chunk in enumerate(retrieved_chunks, start=1):
            if not isinstance(chunk, dict):
                raise ValueError("Every retrieved chunk must be a dictionary.")

            chunk_id = chunk.get("chunk_id")
            chunk_text = chunk.get("text")
            distance = chunk.get("distance")
            metadata = chunk.get("metadata") or {}
            is_cited = chunk.get("is_cited", False)

            if not chunk_id:
                raise ValueError(
                    f"Retrieved chunk at rank {rank} has no chunk_id."
                )

            if not isinstance(chunk_text, str):
                raise ValueError(
                    f"Retrieved chunk at rank {rank} has no valid text."
                )

            if not isinstance(is_cited, bool):
                raise ValueError(
                    f"is_cited for chunk at rank {rank} must be True or False."
                )

            chunk_rows.append((
                interaction_id,
                str(chunk_id),
                rank,
                chunk_text,
                distance,
                json.dumps(metadata, ensure_ascii=False, default=str),
                int(is_cited)
            ))

        if chunk_rows:
            conn.executemany("""
                INSERT INTO interaction_chunks
                    (
                        interaction_id,
                        chunk_id,
                        chunk_rank,
                        chunk_text,
                        distance,
                        metadata,
                        is_cited
                    )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, chunk_rows)

        return interaction_id


def save_feedback(interaction_id, is_helpful, comment=None):
    """
    Save one feedback submission per interaction.

    is_helpful must be:
      True  = thumbs-up / Good
      False = thumbs-down / Bad

    An optional comment can be saved with the rating.
    A second submission for the same interaction is rejected.
    """
    if not isinstance(is_helpful, bool):
        raise ValueError("is_helpful must be Boolean: True or False.")

    if comment is not None:
        if not isinstance(comment, str):
            raise ValueError("Comment must be text or None.")

        comment = comment.strip()[:1000]
        if not comment:
            comment = None

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        try:
            conn.execute("""
                INSERT INTO feedback
                    (interaction_id, is_helpful, comment, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                interaction_id,
                int(is_helpful),
                comment,
                now
            ))
        except sqlite3.IntegrityError as exc:
            # Includes duplicate feedback and invalid interaction IDs.
            raise ValueError(
                "Feedback could not be saved. Check the interaction ID "
                "and whether feedback has already been submitted."
            ) from exc
