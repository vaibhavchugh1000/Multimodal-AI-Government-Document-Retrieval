# Phase 1 — Scalable, Incremental Document Ingestion

## 1. Purpose and scope

Phase 1 improves the efficiency and reliability of document ingestion and vector storage in the existing Government Document RAG application. It introduces content-based change detection, stable document identification, batched embedding generation, batched ChromaDB upserts, and removal of obsolete chunks after a successful update.

The existing Flask application, document loaders, page-level PDF processing approach, chunking strategy, multilingual embedding model, and ChromaDB collection remain the foundation. Phase 1 does **not** redesign the multimodal page-understanding pipeline or introduce a new embedding model.

## 2. Existing multimodal document-processing architecture

Before the scalability operations described in this document, a PDF is processed page by page. Each page is inspected and routed according to its content:

| Page content | Existing processing path | Result passed downstream |
|---|---|---|
| Native-text page | Extract text using `page.get_text()` | Native PDF text |
| Image-oriented page | Extract embedded images; apply OCR and image-level Vision | OCR text and image descriptions, together with any native text |
| Complex visual page | Render the complete page and apply page-level Vision | Native text and a description of the complete page/layout |

**Image-level Vision** interprets an individual embedded image. **Page-level Vision** interprets a rendered page as a whole, helping capture relationships among headings, tables, rows, columns, diagrams, and other visual elements.

The current integrated `pdf_loader.py` stores the resulting page content in a unified `text` field. It also attaches page and source metadata, including `page_number`, `document_id`, `document_name`, `document_path`, `document_type`, `text_source`, `has_images`, `image_count`, `drawing_count`, and `page_type`.

This page-level processing is an upstream capability. Phase 1 focuses on what happens after the loaders produce records: cleaning, chunking, embedding, and storage. The separate *Complete Page-Level Processing Pipeline* document remains the detailed reference for the extraction and vision architecture.

### Page-level processing diagram

The diagram below captures the page-inspection and routing design described in the project's *Complete Page-Level Processing Pipeline*. It shows the three processing paths converging into a unified page representation before the existing cleaning, chunking, embedding, and retrieval workflow.

```mermaid
flowchart TD
    A[Government PDF] --> B[Inspect each page<br/>Native text • embedded images • vector drawings • layout]
    B --> C{Classify page content}

    C -->|Native text| D[Extract native text<br/>page.get_text()]
    C -->|Embedded image content| E[Extract embedded image<br/>image bytes]
    C -->|Complex visual layout| F[Render complete page<br/>page.get_pixmap()]

    E --> G[OCR<br/>Recover text from image]
    E --> H[Image-level Vision<br/>Describe individual image]
    F --> I[Page-level Vision<br/>Interpret full-page layout and relationships]

    D --> J[Build unified page record]
    G --> J
    H --> J
    I --> J

    J --> K[Clean and chunk<br/>Preserve page/document metadata]
    K --> L[Multilingual embedding model<br/>paraphrase-multilingual-MiniLM-L12-v2]
    L --> M[ChromaDB<br/>Vectors + source/page metadata]
    M --> N[Retrieval and grounded answer generation]
```

**Interpretation:** OCR recovers text embedded in images; image-level Vision describes an individual image; page-level Vision analyzes the complete rendered page so that layout and relationships—such as table rows and columns—can be considered together. These are distinct processing paths, not interchangeable operations. The current integrated loader combines their textual outputs into the page record's `text` field.

**Implementation note:** the diagram deliberately does not show language detection as an implemented processing stage. Although the wider architecture document discusses a multilingual layer, language detection and per-page language metadata have not been established in the integrated files reviewed for Phase 1. The multilingual embedding model is used downstream.

## 3. Page-record and chunk metadata contract

The loader-to-ingestion interface is a list of records. For PDF pages, each record currently contains:

```python
{
    "text": "combined page text and/or vision-derived content",
    "page_number": 1,
    "document_id": "document identifier",
    "document_name": "source.pdf",
    "document_path": "path/to/source.pdf",
    "document_type": "pdf",
    "text_source": "pdf_text / ocr+image_vision / pdf_text+page_vision",
    "has_images": False,
    "image_count": 0,
    "drawing_count": 0,
    "page_type": "text / image / complex"
}
```

The admin pipeline adds document-level fields before chunking: `document_hash` and `source_modified_time`, and it assigns the stable `document_id` generated for the source file. The chunker splits each record's `text` into overlapping chunks and uses `record.copy()` so the record's metadata is carried into each chunk. Each chunk receives a `chunk_id`.

This is an important contract: scalability changes must not discard the page number, source type, page classification, or document identity. Those fields support source traceability and help explain where retrieved content originated.

**Current implementation boundary:** the integrated PDF loader combines native text and OCR/Vision output into the record's single `text` field; it does not currently expose separate `native_text`, `ocr_text`, `image_descriptions`, and `page_description` fields. Similarly, language detection and a per-record `language` metadata field are not established by the integrated files reviewed for this phase. The multilingual capability currently comes from the embedding model identified below; language detection/metadata can be treated as a separate future enhancement if implemented and tested.

## 4. Phase 1 changes

- `ingestion_utils.py` — streaming SHA-256 file hashing and stable path-based document IDs.
- `admin_pipeline.py` — validate source files, skip unchanged content, reprocess changed content, and prune obsolete chunks only after current chunks have been upserted successfully.
- `vector_store.py` — validate chunk metadata, write in batches using ChromaDB `upsert`, retrieve existing document metadata, and remove stale chunks.
- `embedding_model.py` — configurable encoding batch size while retaining the existing multilingual model.
- `tests/test_scalability_phase1.py` — automated tests for hashing, IDs, batched writes, metadata validation, and stale-chunk cleanup.

## 5. Document identity and content hashing

The ingestion pipeline calculates a SHA-256 hash by streaming the source file. This avoids reading the entire file into a second in-memory byte buffer. A stable document ID is generated from the source path, allowing repeated versions of the same source document to use consistent chunk identifiers.

The content hash is compared with the hash stored in existing ChromaDB metadata:

- If the hash matches, the document is unchanged and ingestion is skipped.
- If the hash differs, the document is processed again and its current chunks are written.
- If no prior metadata exists, the document is treated as a new ingestion.

Older vectors created before `document_hash` was stored may not be recognized as unchanged. Their next ingestion is expected to reprocess them and add the hash metadata.

## 6. Incremental ingestion lifecycle

1. **Validate:** check the extension and confirm that the source file exists.
2. **Identify:** calculate the file hash and stable document ID.
3. **Compare:** retrieve existing metadata for the source path and compare its stored hash.
4. **Skip unchanged files:** return a skipped result when the content hash matches.
5. **Load changed/new files:** call the appropriate PDF, DOCX, or TXT loader.
6. **Enrich records:** assign consistent document-level metadata while retaining page-specific metadata supplied by the loader.
7. **Clean and chunk:** remove unusable content and split valid records into chunks.
8. **Embed:** generate vectors in configurable model batches.
9. **Upsert:** write current chunks to ChromaDB in bounded batches.
10. **Prune:** after the upsert operation completes, delete obsolete chunk IDs belonging to that source path.
11. **Report:** return a structured status such as `processed`, `updated`, `skipped`, or `empty`.

The ordering of steps 8–10 is intentional: stale chunks are not pruned before current chunks have been written. If loading or embedding fails before storage begins, the previous stored vectors are left untouched. ChromaDB writes across multiple batches are not a single database transaction; a storage failure partway through the upsert can therefore leave a partially updated set. This limitation should be considered in recovery testing rather than described as fully atomic replacement.

## 7. Embedding and vector storage configuration

The integrated embedding module retains:

```python
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

Embedding generation uses a configurable default `batch_size=64`. The progress bar is enabled automatically for inputs larger than one batch unless explicitly overridden.

The integrated vector store retains the local persistent ChromaDB configuration:

```python
CHROMA_PATH = "vector_db/chroma"
COLLECTION_NAME = "government_documents"
DEFAULT_WRITE_BATCH_SIZE = 256
```

Chunks are written using `collection.upsert()` in batches of up to 256. Upsert allows a chunk with an existing ID to be updated instead of creating a duplicate record. Metadata is validated and includes the available document identity, source, page, and processing fields.

## 8. Failure handling and recovery considerations

- If the file is missing or has an unsupported extension, ingestion should fail validation before modifying the vector store.
- If loading produces no usable records, or chunking produces no chunks, the pipeline returns an `empty` result and does not prune existing vectors.
- If embedding generation fails before upsert, existing vectors remain untouched because pruning has not started.
- If an upsert fails partway through its batches, some current chunks may already have been written. The operation is not transactional; rerunning ingestion should be included in recovery tests.
- Stale chunks are pruned only after the current upsert call completes.
- The prune helper rejects `None` or an empty active-ID list to guard against accidental deletion of every chunk for a document.

## 9. Requirements and execution

No new runtime packages are introduced by this phase. It uses the project's existing `chromadb` and `sentence-transformers` dependencies. The phase tests use Python's built-in `unittest` framework and a fake ChromaDB collection for isolated storage tests.

From the repository root, with the project's virtual environment activated:

```bash
python -m unittest discover -s tests -p "test_scalability_phase1.py" -v
python app.py
```

Then use the admin interface to test a PDF, DOCX, or TXT document:

1. Upload a new document and confirm that it is processed.
2. Upload the exact same file again and confirm that it is skipped.
3. Change the document content and upload it again; confirm that it is reprocessed and obsolete chunks are removed.
4. Test a document that produces no usable text and confirm that existing vectors are not pruned.
5. Test a failure during loading/embedding and confirm that the previous stored vectors remain available.
6. Simulate or test a failure during batched upsert and verify the documented recovery behavior.

## 10. Limitations and future improvements

- **Full-document PDF processing:** the integrated `pdf_loader.py` reviewed for this project iterates over all pages; it does not contain the six-page processing cap mentioned in an earlier version of this phase note. Full-document processing can increase OCR/Vision API usage and runtime, so representative long PDFs should be tested.
- **Language metadata:** the current integrated files reviewed here do not establish language detection or a `language` metadata field. Adding language detection, storing language metadata, and applying language-aware retrieval filters should be a separately scoped and tested enhancement.
- **Separate page representations:** the current PDF loader combines extracted and vision-derived content into `text`. Persisting separate fields for native text, OCR text, image descriptions, and page descriptions may improve diagnostics and future retrieval controls, but is not required for the current Phase 1 ingestion changes.
- **Performance measurement:** no benchmark or throughput improvement is claimed yet. Measure ingestion time, embedding time, vector-write time, memory use, and behavior on documents of different sizes before making performance claims.
- **Production validation:** automated tests and manual tests must be run against the actual project environment and representative documents. This document does not claim that those tests have already passed.

## 11. Phase 1 outcome

Phase 1 adds a more controlled ingestion and storage lifecycle around the existing document-understanding pipeline. Its key outcomes are content-based skip detection, stable document identity, configurable batched embeddings, batched vector upserts, and cleanup of obsolete chunks after successful writes—while preserving page-level provenance metadata needed by the RAG retrieval and evidence workflow.
