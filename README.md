# Multimodal AI Framework for OCR-Based Digitization and Intelligent Retrieval of Government Documents

An agentic multimodal AI framework for digitizing, understanding, and intelligently retrieving information from government documents using OCR, computer vision, embeddings, vector databases, and Retrieval-Augmented Generation (RAG).

## Overview

Government documents often contain a mixture of machine-readable text, scanned pages, images, tables, handwritten annotations, and complex layouts. Traditional text-based document retrieval systems may fail to capture information present in these non-text elements.

This project extends a conventional NLP-based RAG system with multimodal document processing capabilities. It identifies the type of content present on each PDF page and applies an appropriate processing method such as direct text extraction, OCR, image understanding, or complete-page vision analysis.

The processed information is converted into searchable representations and stored in a vector database. Users can then ask questions in natural language and receive answers grounded in the available government documents.

## Key Features

* **Multimodal PDF Processing** – Handles text-based, image-based, and complex PDF pages.
* **OCR-Based Digitization** – Extracts text from scanned document pages using Tesseract OCR.
* **Vision-Based Understanding** – Uses a vision-capable LLM to interpret images, tables, layouts, and other visual information.
* **Page-Level Classification** – Determines the appropriate processing strategy for each PDF page.
* **Multi-Format Support** – Supports PDF, DOCX, and TXT documents.
* **Semantic Search** – Uses multilingual sentence embeddings for document retrieval.
* **Vector Database** – Stores document chunks and embeddings in ChromaDB.
* **Retrieval-Augmented Generation** – Retrieves relevant document context before generating an answer.
* **Multilingual Query Support** – Detects the user's query language and generates responses in the detected language.
* **Source Traceability** – Maintains document and page metadata for identifying retrieved sources.
* **Admin/User Workflows** – Provides separate interfaces for document processing and user queries.

## System Architecture

```text
                    Government Documents
                            │
                 ┌──────────┴──────────┐
                 │                     │
             PDF / DOCX / TXT          │
                 │                     │
                 ▼                     │
          Document Processing          │
                 │                     │
        ┌────────┴─────────┐           │
        │                  │           │
     PDF Pages          DOCX/TXT       │
        │                  │           │
        ▼                  │           │
   Page Inspection         │           │
        │                  │           │
        ▼                  │           │
   Page Classification     │           │
        │                  │           │
   ┌────┼────────┐         │           │
   │    │        │         │           │
 Text Image   Complex      │           │
   │    │        │         │           │
   │   OCR    Page Vision  │           │
   │    │        │         │           │
   └────┴────────┘         │           │
          │                │           │
          └───────┬────────┘           │
                  ▼                    │
             Cleaned Text             │
                  │                    │
               Chunking               │
                  │                    │
             Embeddings               │
                  │                    │
               ChromaDB               │
                  │                    │
                  └─────────┬──────────┘
                            │
                       User Query
                            │
                            ▼
                    Language Detection
                            │
                            ▼
                    Semantic Retrieval
                            │
                            ▼
                    Prompt Construction
                            │
                            ▼
                       Gemini LLM
                            │
                            ▼
                 Answer + Sources
```

## Processing Pipeline

### Document Ingestion

1. An administrator uploads a PDF, DOCX, or TXT document.
2. The document type is identified.
3. The appropriate document loader extracts the available content.

### Multimodal PDF Processing

For PDF documents, each page is inspected for:

* Extractable text
* Embedded images
* Drawings and graphical elements

The page is classified into one of three categories:

**Text Page**

Direct PDF text extraction is used.

**Image Page**

OCR is performed using Tesseract, followed by image-level vision analysis.

**Complex Page**

The complete page is rendered as an image and analyzed using a vision-capable Gemini model while retaining available PDF text.

### Retrieval Pipeline

The processed content is:

```text
Cleaning
   ↓
Chunking
   ↓
Embedding Generation
   ↓
ChromaDB
   ↓
Semantic Retrieval
   ↓
Prompt Construction
   ↓
Gemini LLM
   ↓
Grounded Answer
```

## Technologies Used

| Component            | Technology                              |
| -------------------- | --------------------------------------- |
| Programming Language | Python                                  |
| Web Framework        | Flask                                   |
| PDF Processing       | PyMuPDF                                 |
| OCR                  | Tesseract OCR / Pytesseract             |
| Image Processing     | Pillow                                  |
| Embeddings           | Sentence Transformers                   |
| Embedding Model      | `paraphrase-multilingual-MiniLM-L12-v2` |
| Vector Database      | ChromaDB                                |
| LLM                  | Google Gemini                           |
| Frontend             | HTML / CSS / JavaScript                 |
| Document Formats     | PDF, DOCX, TXT                          |

## Project Structure

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
├── cleaner.py
├── chunker.py
│
├── page_classifier.py
├── ocr_processor.py
├── vision_processor.py
│
├── embedding_model.py
├── vector_store.py
├── retriever.py
├── prompt_builder.py
├── llm_engine.py
├── language_detector.py
│
├── gui/
│   ├── login.html
│   ├── admin.html
│   └── user.html
│
├── project_documents/
│
├── requirements.txt
├── BASELINE.md
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/vaibhavchugh1000/Multimodal-AI-Government-Document-Retrieval.git
cd Multimodal-AI-Government-Document-Retrieval
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root and add the Gemini API key:

```text
Gemini_API_Key=YOUR_GEMINI_API_KEY
```

Tesseract OCR should also be installed and configured on the system.

## Running the Application

Start the Flask application:

```bash
python app.py
```

The application runs locally at:

```text
http://127.0.0.1:5000
```

## Application Workflow

### Admin

```text
Login
  ↓
Admin Interface
  ↓
Upload Government Document
  ↓
Document Processing
  ↓
OCR / Vision Processing
  ↓
Chunking & Embeddings
  ↓
ChromaDB
```

### User

```text
Login
  ↓
User Interface
  ↓
Enter Question
  ↓
Language Detection
  ↓
Semantic Retrieval
  ↓
Context Construction
  ↓
Gemini LLM
  ↓
Answer + Sources
```

## Research Direction

The project is designed as a foundation for research into intelligent processing of large collections of government documents.

Future development includes:

* Scalable processing of hundreds or thousands of documents
* Improved page-level document understanding
* Better table and layout understanding
* Advanced multimodal retrieval
* Self-improving document knowledge and retrieval mechanisms
* Agentic document-processing workflows
* Improved source attribution and answer verification
* Evaluation of OCR, retrieval, and answer-generation performance
* Support for additional Indian languages

## Project Objective

The primary objective is to develop a multimodal AI framework that can transform heterogeneous government documents into searchable and understandable knowledge while enabling users to retrieve reliable information through natural-language queries.

## License

This project is developed for academic and research purposes.
