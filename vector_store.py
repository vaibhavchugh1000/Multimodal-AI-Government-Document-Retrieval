"""Persistent ChromaDB storage with batched, idempotent writes."""

import chromadb

CHROMA_PATH = "vector_db/chroma"
COLLECTION_NAME = "government_documents"
DEFAULT_WRITE_BATCH_SIZE = 256

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


def _metadata_for_chunk(chunk):
    """Build Chroma-compatible scalar metadata, omitting missing values."""
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
    metadata = {key: chunk[key] for key in keys if chunk.get(key) is not None}
    required = ("document_id", "document_name", "document_path", "document_type")
    missing = [key for key in required if key not in metadata]
    if missing:
        raise ValueError(f"Chunk is missing required metadata: {', '.join(missing)}")
    return metadata


def add_documents(chunks, embeddings, batch_size=DEFAULT_WRITE_BATCH_SIZE):
    """Upsert chunks in bounded batches so repeated ingestion is safe."""
    if not chunks:
        raise ValueError("Chunks cannot be empty.")
    if len(chunks) != len(embeddings):
        raise ValueError("Number of chunks must match number of embeddings.")
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")

    for start in range(0, len(chunks), batch_size):
        end = min(start + batch_size, len(chunks))
        batch_chunks = chunks[start:end]
        batch_embeddings = embeddings[start:end]
        documents = [chunk["text"] for chunk in batch_chunks]
        metadatas = [_metadata_for_chunk(chunk) for chunk in batch_chunks]
        ids = [chunk["chunk_id"] for chunk in batch_chunks]
        vectors = batch_embeddings.tolist() if hasattr(batch_embeddings, "tolist") else [list(v) for v in batch_embeddings]

        collection.upsert(
            documents=documents,
            embeddings=vectors,
            metadatas=metadatas,
            ids=ids,
        )

    print(f"stored or updated {len(chunks)} document chunks")


def get_document_metadata(document_path):
    """Return metadata for one existing chunk at a document path, if present."""
    result = collection.get(
        where={"document_path": str(document_path)},
        include=["metadatas"],
        limit=1,
    )
    metadatas = result.get("metadatas") or []
    return metadatas[0] if metadatas else None


def prune_document_chunks(document_path, active_chunk_ids):
    """Remove stale chunks for a path after all current chunks were upserted."""
    result = collection.get(
        where={"document_path": str(document_path)},
        include=["metadatas"],
    )
    existing_ids = result.get("ids") or []
    active_ids = set(active_chunk_ids)
    stale_ids = [chunk_id for chunk_id in existing_ids if chunk_id not in active_ids]
    if stale_ids:
        collection.delete(ids=stale_ids)
    return len(stale_ids)
