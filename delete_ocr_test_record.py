from vector_store import collection


count=collection.delete(
    where={
        "document_id": "citizen-charter-2024-25-1"
    }
)

print("OCR test document deleted from ChromaDB.")
print("no of records deleted from ChromaDB = ",count)