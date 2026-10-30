# Phase 1 — Scalable, Incremental Document Ingestion

This phase keeps the existing Flask app, loaders, chunker, MiniLM model, and ChromaDB collection. It changes ingestion/storage behavior only.

## Changes

- `ingestion_utils.py` — streaming SHA-256 file hashing and stable path-based document IDs.
- `admin_pipeline.py` — skip unchanged content; re-index changed content; retain prior vectors when loading/embedding fails; prune stale chunks after successful upserts.
- `vector_store.py` — batched ChromaDB `upsert`, metadata validation, content hash metadata, and stale-chunk cleanup helpers.
- `embedding_model.py` — configurable encoding batch size while retaining `paraphrase-multilingual-MiniLM-L12-v2`.
- `tests/test_scalability_phase1.py` — tests hashing, IDs, batched writes, metadata validation, and stale-chunk cleanup.

## Requirements

No new runtime packages are required. The existing `chromadb` and `sentence-transformers` dependencies are used. Tests use Python's built-in `unittest` and a fake Chroma collection.

## Apply the files

Copy the files from this phase package into the repository, preserving the `tests/` directory. These files replace the existing `admin_pipeline.py`, `vector_store.py`, and `embedding_model.py` and add `ingestion_utils.py` and the test file.

## Run

From the repository root, with the project's existing virtual environment activated:

```bash
python -m unittest discover -s tests -p "test_scalability_phase1.py" -v
python app.py
```

Then upload a PDF, DOCX, or TXT through the admin workflow. Upload the exact same file again (it should be skipped), then edit its content and upload it again (it should be re-indexed and stale chunks pruned).

## Notes and limitations

- The SHA-256 hash is calculated by streaming the file, avoiding a second full-file memory copy.
- Chunks are upserted in batches of 256; embeddings are generated with model batches of 64. These are configurable defaults.
- ChromaDB is still a local persistent database at `vector_db/chroma`.
- The repository's current PDF loader has a six-page processing cap. This phase does not silently remove that cap; full-document PDF processing should be a separately tested loader change because it can increase OCR/vision API calls and runtime significantly.
- Existing vectors created before this phase do not have `document_hash`; their first subsequent ingestion will reprocess them to add the hash.
- This phase has not run against your local documents or production ChromaDB in this environment. Benchmark claims are intentionally not made.
