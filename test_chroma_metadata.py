from vector_store import collection


results = collection.get(
    where={
        "document_id": "scanned_test_document"
    },
    include=["documents", "metadatas"]
)


print("\n========== OCR CHROMADB METADATA TEST ==========\n")

print("Number of records found:", len(results["ids"]))

for i, metadata in enumerate(results["metadatas"]):

    print("\n-----------------------------------")
    print("Record:", i + 1)
    print("Metadata:", metadata)
    print("Text source:", metadata.get("text_source"))

    print("\nStored text:")
    print(results["documents"][i])