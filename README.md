# Multimodal AI Government Document Retrieval

An **agentic multimodal AI framework for OCR-based digitization and intelligent retrieval of government documents using Retrieval-Augmented Generation (RAG).**

The system is designed to process government documents in different formats, including text-based and scanned PDFs, extract and understand their contents using OCR and document/image processing, store the extracted information as semantic embeddings, and provide grounded answers to user queries through a RAG pipeline.

---

## 📌 Overview

Government documents often contain information in different forms, including:

- Digitally generated text
- Scanned documents
- Images
- Tables
- Structured and unstructured content
- Documents in multiple Indian languages

Traditional text-only document retrieval systems may fail when important information exists inside scanned pages or images.

This project addresses this problem by combining:

**Document Processing + OCR + Text Processing + Embeddings + Vector Search + LLM-based Question Answering**

The system allows an administrator to upload government documents and enables users to ask natural-language questions about the uploaded documents.

---

## 🚀 Key Features

### 1. Multimodal Document Processing

The system can process different types of government documents, including:

- PDF
- DOCX
- TXT
- Text-based PDFs
- Scanned/image-based PDFs

The document processing pipeline determines the appropriate extraction approach depending on the document content.

---

### 2. OCR-Based Digitization

For scanned documents and pages containing images, OCR is used to extract machine-readable text.

The OCR pipeline uses:

- **Tesseract OCR**
- **PyMuPDF**
- **Pillow**
- Image preprocessing

This allows information from scanned government documents to become searchable through the RAG system.

---

### 3. Text Extraction and Cleaning

Extracted document content is cleaned and normalized before being passed to the retrieval pipeline.

The system handles:

- PDF text extraction
- DOCX text extraction
- TXT files
- OCR-generated text
- Text cleaning
- Page-level document information

---

### 4. Semantic Chunking

Documents are divided into smaller chunks before embedding.

Chunking allows the retrieval system to identify the most relevant sections of a document instead of processing the entire document for every query.

---

### 5. Multilingual Embeddings

The project uses:

```text
paraphrase-multilingual-MiniLM-L12-v2
```

to generate semantic embeddings.

This provides multilingual semantic representation for government documents and user queries.

---

### 6. Vector Database

The extracted document chunks are stored in **ChromaDB** as vector embeddings.

The vector database enables semantic similarity search between:

```text
User Query
     ↓
Query Embedding
     ↓
Vector Similarity Search
     ↓
Relevant Document Chunks
```

---

### 7. Retrieval-Augmented Generation

The retrieved document chunks are passed to the LLM as contextual evidence.

The overall RAG pipeline is:

```text
User Query
     ↓
Query Processing
     ↓
Query Embedding
     ↓
ChromaDB Retrieval
     ↓
Relevant Document Chunks
     ↓
Prompt Construction
     ↓
Gemini LLM
     ↓
Grounded Answer
```

The objective is to generate answers based on the contents of the uploaded government documents rather than relying only on the LLM's pretrained knowledge.

---

### 8. Source-Aware Responses

Retrieved document information is preserved as part of the response pipeline so that answers can be associated with the relevant source documents.

This improves transparency and allows users to understand where the information used for an answer originated.

---

### 9. Multilingual Query Support

The system includes language detection for multiple Indian languages, including:

- English
- Hindi
- Tamil
- Telugu
- Bengali
- Marathi
- Gujarati
- Kannada
- Malayalam
- Punjabi
- Urdu
- Odia
- Assamese

This allows the system to support multilingual government-document retrieval.

---

### 10. Document Management

The administrator interface provides functionality for uploading and processing government documents.

The system also maintains document information required for ingestion and retrieval.

Duplicate document handling is included to prevent unnecessary re-processing of the same uploaded document.

---

### 11. Feedback Collection

The application includes a feedback mechanism that allows users to provide feedback on generated answers.

Feedback can be used to study:

- Answer quality
- User satisfaction
- Retrieval failures
- Incorrect or incomplete responses
- Areas for future improvement

This feedback mechanism forms the foundation for future development of a **feedback-driven self-learning retrieval system**.

---

### 12. Scalability Improvements

The ingestion pipeline includes mechanisms for more efficient document processing, including:

- Stable document identification
- Duplicate detection
- Document update handling
- Stale chunk removal
- Batched vector upserts
- Configurable embedding batch processing

These mechanisms reduce unnecessary re-processing when documents are uploaded or updated.

---

## 🏗️ System Architecture

The overall architecture can be represented as:

```text
                  ┌─────────────────────┐
                  │ Government Documents│
                  │ PDF / DOCX / TXT    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Document Processing │
                  └──────────┬──────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
       Text Extraction                 OCR Processing
       PDF / DOCX / TXT                Scanned Pages
              │                             │
              └──────────────┬──────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Text Cleaning  │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │    Chunking    │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │   Embeddings   │
                    │  MiniLM Model  │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │    ChromaDB    │
                    │ Vector Storage │
                    └───────┬────────┘
                            │
                            │
                    ┌───────▼────────┐
                    │   User Query   │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │ Query Embedding│
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │    Retriever   │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │ Relevant Chunks│
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │ Prompt Builder │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │  Gemini LLM    │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │ Grounded Answer│
                    │  + Sources     │
                    └────────────────┘
```

---

## 🔄 Document Ingestion Workflow

When an administrator uploads a document:

```text
Upload Document
      ↓
Validate File
      ↓
Detect Document Type
      ↓
Extract Text / Perform OCR
      ↓
Clean Extracted Content
      ↓
Split into Chunks
      ↓
Generate Embeddings
      ↓
Store in ChromaDB
      ↓
Document Available for Retrieval
```

For scanned PDFs, OCR is applied to pages where machine-readable text is not available or where image-based content requires extraction.

---

## 🔎 Query Workflow

When a user asks a question:

```text
User Question
      ↓
Language Detection
      ↓
Query Embedding
      ↓
Semantic Similarity Search
      ↓
Retrieve Relevant Chunks
      ↓
Build Context
      ↓
Send Context + Query to Gemini
      ↓
Generate Answer
      ↓
Display Answer + Source Information
```

---

## 🧠 Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python |
| Web Framework | Flask |
| OCR | Tesseract OCR |
| PDF Processing | PyMuPDF |
| DOCX Processing | python-docx |
| Image Processing | Pillow |
| Embeddings | `paraphrase-multilingual-MiniLM-L12-v2` |
| Vector Database | ChromaDB |
| LLM | Google Gemini |
| Frontend | HTML / CSS |
| Environment | Python Virtual Environment |

---

## 📁 Project Structure

```text
Multimodal-AI-Government-Document-Retrieval/
│
├── app.py
├── admin_pipeline.py
├── user_pipeline.py
│
├── pdf_loader.py
├── docx_loader.py
├── txt_loader.py
│
├── ocr_processor.py
├── vision_processor.py
├── page_classifier.py
│
├── cleaner.py
├── chunker.py
├── ingestion_utils.py
│
├── embedding_model.py
├── vector_store.py
├── retriever.py
│
├── language_detector.py
├── prompt_builder.py
├── llm_engine.py
│
├── feedback_store.py
├── source_checker.py
│
├── get_directory_documents.py
│
├── gui/
│   ├── admin.html
│   └── user.html
│
├── test/
│   ├── test_ocr_processor.py
│   ├── test_pdf_loader.py
│   ├── test_retriever.py
│   ├── test_vision.py
│   └── ...
│
├── project_documents/
│
├── requirements.txt
├── BASELINE.md
└── SCALABILITY_PHASE1.md
```

The current repository contains dedicated OCR, vision, retrieval, vector-store, feedback, and testing components.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/vaibhavchugh1000/Multimodal-AI-Government-Document-Retrieval.git
```

```bash
cd Multimodal-AI-Government-Document-Retrieval
```

---

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create a `.env` file in the project root.

Add the required Gemini API configuration:

```env
GEMINI_API_KEY=your_api_key_here
```

Do not commit API keys or other credentials to GitHub.

---

## ▶️ Running the Application

Start the Flask application:

```bash
python app.py
```

The application will start locally.

Open the displayed local Flask URL in a web browser.

---

## 👨‍💼 Admin Workflow

The administrator can:

1. Open the admin interface.
2. Upload government documents.
3. Process the documents.
4. Extract text and/or perform OCR.
5. Generate document chunks.
6. Generate embeddings.
7. Store embeddings in ChromaDB.
8. Make documents available for user queries.

---

## 👤 User Workflow

Users can:

1. Open the user interface.
2. Enter a natural-language question.
3. The system generates a query embedding.
4. Relevant document chunks are retrieved.
5. Retrieved information is passed to Gemini.
6. The system generates a grounded response.
7. Relevant source information is displayed with the answer.

---

## 🧪 Testing

The repository includes tests for important components of the system, including:

- OCR processing
- PDF loading
- Vision processing
- Document metadata
- Retriever behaviour
- Prompt construction
- LLM functionality
- ChromaDB/vector storage
- Admin document processing

Tests can be run using Python's testing framework.

Example:

```bash
python -m unittest discover
```

Individual tests can also be executed directly, for example:

```bash
python test_ocr_processor.py
```

---

## 🔐 Reliability and Document Validation

Government documents require additional reliability considerations.

The project includes a source/document checking component intended to support validation of document information before it enters the retrieval pipeline.

Future versions can further extend this layer with:

- Official-source verification
- Document authenticity checks
- Malware/virus scanning
- File integrity checks
- Digital signature verification
- Source-domain validation

---

## 📈 Scalability

The ingestion pipeline includes Phase 1 scalability improvements.

The system can identify documents consistently and avoid unnecessary processing when an unchanged document is uploaded again.

The scalability design also considers:

- Duplicate document detection
- Changed-document updates
- Stale vector removal
- Batched embedding generation
- Batched vector database operations

See:

```text
SCALABILITY_PHASE1.md
```

for additional implementation details.

---

## 🔮 Future Enhancements

Planned and potential future improvements include:

### Adaptive Chunking

Replace fixed chunk sizes with **query-aware and content-aware adaptive chunking**, where chunk size and boundaries can change depending on the user's query and the structure/relevance of the document.

### Improved OCR

Future OCR improvements may include:

- Better image preprocessing
- Layout-aware OCR
- Table extraction
- Handwritten text recognition
- Improved multilingual OCR
- Confidence-based OCR selection

### Advanced Multimodal Retrieval

Future versions can improve retrieval across:

- Text
- Tables
- Images
- Charts
- Document layouts

### Feedback-Driven Learning

User feedback can be used to identify retrieval and generation failures and continuously improve the system.

This forms the basis for a future:

**Feedback-Driven Self-Learning Agent for OCR-Based Retrieval-Augmented Generation Systems.**

### Security

Potential security improvements include:

- Malware scanning
- File type validation
- Content sanitization
- Secure document storage
- Authentication and authorization
- API security

---

## 📚 Research Direction

This project also provides a foundation for research into feedback-driven improvement of multimodal RAG systems.

A potential research direction is:

> **A Feedback-Driven Self-Learning Agent for Continuous Improvement of OCR-Based Retrieval-Augmented Generation Systems for Government Documents**

The research can investigate how user feedback, retrieval errors, OCR quality, and answer evaluation can be used to improve the system continuously.

---

## 🎯 Project Objective

The primary objective of this project is to build a reliable and intelligent document retrieval system capable of working with complex government documents, including scanned and image-based documents.

The system combines:

```text
OCR
 +
Multimodal Document Processing
 +
Semantic Embeddings
 +
Vector Retrieval
 +
Retrieval-Augmented Generation
 +
LLM
```

to provide users with a more accessible way to search and obtain information from government documents.

---

## 👥 Contributors

- **Vaibhav Chugh**
- **Srivatsan Raghavan**

---
## 📄 License

This project is intended for academic and research purposes.
