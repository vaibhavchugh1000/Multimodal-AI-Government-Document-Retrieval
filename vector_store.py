import chromadb


CHROMA_PATH = "vector_db/chroma"
COLLECTION_NAME = "government_documents"


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


def add_documents(chunks, embeddings):
    """
    Store document chunks, embeddings, and metadata in ChromaDB.

    Args:
        chunks: List of chunk records.
        embeddings: Embedding vectors corresponding to the chunks.

    Returns:
        None
    """

    if not chunks:
        raise ValueError("Chunks cannot be empty.")

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks must match number of embeddings."
        )

    documents = []
    metadatas = []
    ids = []

    for chunk in chunks:

        documents.append(chunk["text"])

        metadata = {
            "document_id": chunk["document_id"],
            "document_name": chunk["document_name"],
            "document_path": chunk["document_path"],
            "document_type": chunk["document_type"]
        }

        if "page_number" in chunk:
            metadata["page_number"] = chunk["page_number"]

        if "paragraph_number" in chunk:
            metadata["paragraph_number"] = chunk["paragraph_number"]

        if "source_text" in chunk : 
            metadata["source_text"]=chunk["source_text"]
        metadatas.append(metadata)

        ids.append(chunk["chunk_id"])

    collection.add(
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
        ids=ids
    )
    
    print("document stored successfully")