"""Utilities for idempotent, incremental document ingestion."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(file_path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Return a SHA-256 digest without loading the whole file into memory."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    digest = hashlib.sha256()
    with Path(file_path).open("rb") as source:
        for chunk in iter(lambda: source.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_document_id(file_path: str | Path) -> str:
    """Create a stable ID for a path, avoiding collisions between equal stems."""
    path = Path(file_path)
    normalized_path = str(path).replace("\\", "/").casefold()
    path_digest = hashlib.sha256(normalized_path.encode("utf-8")).hexdigest()[:12]
    return f"{path.stem}_{path_digest}"
