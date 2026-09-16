# NLP RAG Baseline

## 1. Purpose

This baseline represents the working NLP-based Government Document
Retrieval system that serves as the foundation for the Final Major Project.

The baseline was migrated from the NLP project into the Major Project
repository and tested successfully before introducing multimodal
capabilities.

---

## 2. Baseline Architecture

The system consists of two main workflows:

### Admin Workflow

Login → Admin GUI → Document Upload → Document Loading → Cleaning →
Chunking → Embedding Generation → ChromaDB

### User Workflow

Login → User GUI → User Query → Query Processing → ChromaDB Retrieval →
Prompt Construction → Gemini LLM → Answer + Detected Language + Sources

---

## 3. Supported Document Types

The baseline supports:

- PDF
- DOCX
- TXT

---

## 4. Document Processing Pipeline

For an uploaded document:

1. The file extension is identified.
2. The appropriate document loader extracts text.
3. Extracted records are cleaned.
4. The document is divided into chunks.
5. Embeddings are generated for the chunks.
6. Chunks, embeddings and metadata are stored in ChromaDB.

---

## 5. Vector Database

The baseline uses ChromaDB for vector storage and semantic retrieval.

The baseline ChromaDB location is:

`vector_db/chroma`

The persisted vector database is intentionally excluded from Git using
`.gitignore`.

---

## 6. Metadata

Document chunks are stored with metadata to support source traceability
and document identification.

Examples include:

- document ID
- document name
- page information where available
- other loader-generated metadata

---

## 7. Language Detection

The baseline detects the language of the user query.

For example:

```text
Query:
What is Component Chapters Journey?

Detected language:
en