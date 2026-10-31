# vector_store module
"""Persistent ChromaDB storage with batched, idempotent writes."""

from pathlib import Path

import chromadb


CHROMA_PATH = "vector_db/chroma"
COLLECTION_NAME = "government_documents"
DEFAULT_WRITE_BATCH_SIZE = 256


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


def _normalize_document_path(document_path):
    """Return a consistent string representation of a document path."""
    return str(Path(document_path))


def _metadata_for_chunk(chunk):
    """
    Build ChromaDB-compatible scalar metadata for one chunk.

    Required fields are validated. Optional fields with None values
    are omitted because ChromaDB metadata values must be scalar.
    """
    keys = (
        "document_id",
        "document_name",
        "document_path",
        "document_type",
        "text_source",
        "page_number",
        "paragraph_number",
        "document_hash",
        "source_modified_time",
        "has_images",
        "image_count",
        "drawing_count",
        "page_type",
    )

    metadata = {
        key: chunk[key]
        for key in keys
        if chunk.get(key) is not None
    }

    required = (
        "document_id",
        "document_name",
        "document_path",
        "document_type",
        "text_source",
    )

    missing = [key for key in required if key not in metadata]

    if missing:
        raise ValueError(
            "Chunk is missing required metadata: "
            + ", ".join(missing)
        )

    metadata["document_path"] = _normalize_document_path(
        metadata["document_path"]
    )

    return metadata


def add_documents(
    chunks,
    embeddings,
    batch_size=DEFAULT_WRITE_BATCH_SIZE,
):
    """
    Store or update document chunks and embeddings in bounded batches.

    Args:
        chunks: List of chunk records.
        embeddings: Embedding vectors corresponding to the chunks.
        batch_size: Maximum number of chunks written in one batch.

    Returns:
        None
    """
    if not chunks:
        raise ValueError("Chunks cannot be empty.")

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks must match number of embeddings."
        )

    if (
        isinstance(batch_size, bool)
        or not isinstance(batch_size, int)
        or batch_size <= 0
    ):
        raise ValueError("batch_size must be a positive integer.")

    for start in range(0, len(chunks), batch_size):
        end = min(start + batch_size, len(chunks))

        batch_chunks = chunks[start:end]
        batch_embeddings = embeddings[start:end]

        documents = [chunk["text"] for chunk in batch_chunks]
        metadatas = [
            _metadata_for_chunk(chunk)
            for chunk in batch_chunks
        ]
        ids = [chunk["chunk_id"] for chunk in batch_chunks]

        vectors = (
            batch_embeddings.tolist()
            if hasattr(batch_embeddings, "tolist")
            else [list(vector) for vector in batch_embeddings]
        )

        collection.upsert(
            documents=documents,
            embeddings=vectors,
            metadatas=metadatas,
            ids=ids,
        )

    print(f"Stored or updated {len(chunks)} document chunks.")


def get_document_metadata(document_path):
    """
    Return metadata for one existing chunk at a document path.

    Returns:
        A metadata dictionary if a matching chunk exists; otherwise None.
    """
    normalized_path = _normalize_document_path(document_path)

    result = collection.get(
        where={"document_path": normalized_path},
        include=["metadatas"],
        limit=1,
    )

    metadatas = result.get("metadatas") or []

    return metadatas[0] if metadatas else None


def prune_document_chunks(document_path, active_chunk_ids):
    """
    Delete stale chunks for a document after current chunks are upserted.

    Args:
        document_path: Path identifying the document in ChromaDB metadata.
        active_chunk_ids: IDs of all chunks generated from the current
            version of the document.

    Returns:
        Number of stale chunks deleted.
    """
    if active_chunk_ids is None:
        raise ValueError(
            "active_chunk_ids cannot be None. "
            "Refusing to delete document chunks."
        )

    active_ids = set(active_chunk_ids)

    if not active_ids:
        raise ValueError(
            "active_chunk_ids cannot be empty. "
            "Refusing to delete all document chunks."
        )

    normalized_path = _normalize_document_path(document_path)

    result = collection.get(
        where={"document_path": normalized_path},
        include=[],
    )

    existing_ids = result.get("ids") or []

    stale_ids = [
        chunk_id
        for chunk_id in existing_ids
        if chunk_id not in active_ids
    ]

    if stale_ids:
        collection.delete(ids=stale_ids)

    return len(stale_ids)
