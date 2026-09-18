from vector_store import collection


# Get a few records from ChromaDB
results = collection.get(
    limit=5,
    include=["documents", "metadatas"]
)


print("\n========== CHROMADB METADATA TEST ==========\n")

for i, metadata in enumerate(results["metadatas"]):

    print(f"Record {i + 1}")
    print("Metadata:", metadata)
    print("Text source:", metadata.get("text_source"))
    print("-----------------------------------")