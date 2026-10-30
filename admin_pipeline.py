"""Admin ingestion pipeline with content-aware incremental processing."""

from pathlib import Path

from pdf_loader import load_pdf
from docx_loader import load_docx
from txt_loader import load_txt
from cleaner import clean_records
from chunker import chunk_records
from embedding_model import create_embeddings
from ingestion_utils import sha256_file, stable_document_id
from vector_store import (
    add_documents,
    collection,
    get_document_metadata,
    prune_document_chunks,
)


def process_document(document_path):
    path = Path(document_path)
    extension = path.suffix.lower()
    path_key = str(path)

    if extension not in {".pdf", ".txt", ".docx"}:
        raise ValueError("invalid extension")
    if not path.is_file():
        raise FileNotFoundError(f"Document does not exist: {path}")

    document_hash = sha256_file(path)
    existing_metadata = get_document_metadata(path_key)
    if existing_metadata and existing_metadata.get("document_hash") == document_hash:
        return {
            "status": "skipped",
            "document_name": path.name,
            "chunks_created": 0,
            "message": "Document content is unchanged; existing vectors were reused.",
            "success": True,
        }

    if extension == ".pdf":
        records = load_pdf(path_key)
    elif extension == ".txt":
        records = load_txt(path_key)
    else:
        records = load_docx(path_key)

    document_id = stable_document_id(path)
    modified_time = int(path.stat().st_mtime)
    for record in records:
        record["document_id"] = document_id
        record["document_name"] = path.name
        record["document_path"] = path_key
        record["document_hash"] = document_hash
        record["source_modified_time"] = modified_time

    cleaned_records = clean_records(records)
    chunks = chunk_records(cleaned_records)
    if not chunks:
        return {
            "status": "empty",
            "document_name": path.name,
            "chunks_created": 0,
            "message": "No extractable text was found; the existing index was left unchanged.",
            "success": False,
        }

    texts = [chunk["text"] for chunk in chunks]
    embeddings = create_embeddings(texts, batch_size=64)

    # Upsert the complete current version first. Only then remove old chunks,
    # so a loader/embedding failure does not erase the previously indexed file.
    add_documents(chunks, embeddings)
    removed_chunks = prune_document_chunks(
        path_key,
        [chunk["chunk_id"] for chunk in chunks],
    )

    print("document processed and stored in vector db successfully")
    return {
        "status": "updated" if existing_metadata else "processed",
        "document_name": path.name,
        "chunks_created": len(chunks),
        "stale_chunks_removed": removed_chunks,
        "document_hash": document_hash,
        "success": True,
    }
