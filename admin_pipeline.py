"""Admin ingestion pipeline for content-aware incremental document processing."""

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
    # --------------------------------------------------
    # 1. Identify and validate the source document
    # --------------------------------------------------
    path = Path(document_path)
    extension = path.suffix.lower()
    path_key = str(path)

    if extension not in {".pdf", ".txt", ".docx"}:
        raise ValueError("invalid extension")

    if not path.is_file():
        raise FileNotFoundError(f"Document does not exist: {path}")

    # --------------------------------------------------
    # 2. Detect unchanged documents using their content hash
    # --------------------------------------------------
    document_hash = sha256_file(path)
    existing_metadata = get_document_metadata(path_key)

    if (
        existing_metadata
        and existing_metadata.get("document_hash") == document_hash
    ):
        return {
            "status": "skipped",
            "document_name": path.name,
            "chunks_created": 0,
            "message": "Document content is unchanged; existing vectors were reused.",
            "success": True,
        }

    # --------------------------------------------------
    # 3. Load the document
    # --------------------------------------------------
    if extension == ".pdf":
        print("calling load_pdf() : ")
        records = load_pdf(path_key)
        document_type = "pdf"

    elif extension == ".txt":
        print("calling load_txt() : ")
        records = load_txt(path_key)
        document_type = "txt"

    elif extension == ".docx":
        print("calling load_docx() : ")
        records = load_docx(path_key)
        document_type = "docx"

    # --------------------------------------------------
    # 4. Assign consistent document metadata
    # --------------------------------------------------
    document_id = stable_document_id(path)
    modified_time = int(path.stat().st_mtime)

    for record in records:
        record["document_id"] = document_id
        record["document_name"] = path.name
        record["document_path"] = path_key
        record["document_type"] = document_type
        record["document_hash"] = document_hash
        record["source_modified_time"] = modified_time

        # Preserve the PDF loader's specific text source.
        # Supply consistent source labels for DOCX and TXT records.
        if document_type == "docx":
            record.setdefault("text_source", "docx_text")
        elif document_type == "txt":
            record.setdefault("text_source", "txt_text")

    # --------------------------------------------------
    # 5. Clean records and generate chunks
    # --------------------------------------------------
    cleaned_records = clean_records(records)

    valid_records = [
        record
        for record in cleaned_records
        if record.get("text") and record["text"].strip()
    ]

    if not valid_records:
        return {
            "status": "empty",
            "document_name": path.name,
            "chunks_created": 0,
            "message": "No extractable text was found; existing vectors were left unchanged.",
            "success": False,
        }

    chunks = chunk_records(valid_records)

    if not chunks:
        return {
            "status": "empty",
            "document_name": path.name,
            "chunks_created": 0,
            "message": "No valid chunks were generated; existing vectors were left unchanged.",
            "success": False,
        }

    # --------------------------------------------------
    # 6. Generate embeddings
    # --------------------------------------------------
    texts = [chunk["text"] for chunk in chunks]
    embeddings = create_embeddings(texts, batch_size=64)

    # --------------------------------------------------
    # 7. Upsert current chunks, then prune obsolete chunks
    # --------------------------------------------------
    add_documents(chunks, embeddings)

    removed_chunks = prune_document_chunks(
        path_key,
        [chunk["chunk_id"] for chunk in chunks],
    )

    print("document processed and stored in vector db successfully")
    print("Stale chunks removed:", removed_chunks)
    print("total vector count present in vector_db = ", collection.count())

    # --------------------------------------------------
    # 8. Return a structured processing result
    # --------------------------------------------------
    status = "updated" if existing_metadata else "processed"
    message = (
        "Document updated successfully."
        if status == "updated"
        else "Document processed and stored successfully."
    )

    return {
        "status": status,
        "document_name": path.name,
        "chunks_created": len(chunks),
        "stale_chunks_removed": removed_chunks,
        "document_hash": document_hash,
        "message": message,
        "success": True,
    }
