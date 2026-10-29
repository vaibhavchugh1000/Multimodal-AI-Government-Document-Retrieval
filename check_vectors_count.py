# check_vectors_count.py

from vector_store import collection


# --------------------------------------------------
# Get stored data from ChromaDB
# --------------------------------------------------

results = collection.get(
    include=["documents", "metadatas", "embeddings"]
)


# --------------------------------------------------
# 1. Check number of stored records
# --------------------------------------------------

print("\n========================================")
print("CHROMADB STORAGE VERIFICATION")
print("========================================")

print("Total stored chunks:", len(results["ids"]))


# --------------------------------------------------
# 2. Check embeddings
# --------------------------------------------------

embeddings = results["embeddings"]

print("\nNumber of stored embeddings:", len(embeddings))

if len(embeddings) > 0 :
    print("Dimension of first embedding:", len(embeddings[0]))


# --------------------------------------------------
# 3. Check documents
# --------------------------------------------------

documents = results["documents"]

print("\nNumber of stored documents/chunks:", len(documents))

if documents:
    print("First chunk text:")
    print(documents[0][:500])


# --------------------------------------------------
# 4. Check metadata
# --------------------------------------------------

metadatas = results["metadatas"]

print("\n========================================")
print("FIRST CHUNK METADATA")
print("========================================")

if metadatas:
    for key, value in metadatas[0].items():
        print(f"{key}: {value}")


# --------------------------------------------------
# 5. Check all expected multimodal metadata fields
# --------------------------------------------------

print("\n========================================")
print("MULTIMODAL METADATA CHECK")
print("========================================")

expected_fields = [
    "document_id",
    "document_name",
    "document_path",
    "document_type",
    "text_source",
    "page_number",
    "page_type",
    "has_images",
    "image_count",
    "drawing_count"
]

if metadatas:

    first_metadata = metadatas[0]

    for field in expected_fields:

        if field in first_metadata:
            print(f"{field}: PRESENT")
        else:
            print(f"{field}: MISSING")


# --------------------------------------------------
# 6. Check embedding/document count consistency
# --------------------------------------------------

print("\n========================================")
print("CONSISTENCY CHECK")
print("========================================")

print("IDs:", len(results["ids"]))
print("Documents:", len(results["documents"]))
print("Embeddings:", len(results["embeddings"]))
print("Metadata:", len(results["metadatas"]))

if (
    len(results["ids"])
    == len(results["documents"])
    == len(results["embeddings"])
    == len(results["metadatas"])
):
    print("\nAll stored components have matching counts.")
else:
    print("\nWARNING: Stored component counts do not match.")
    
    
    
    
    
# --------------------------------------------------
# 7. Verify metadata values for each page type
# --------------------------------------------------

print("\n========================================")
print("PAGE TYPE METADATA VERIFICATION")
print("========================================")


page_types = ["text", "image", "complex"]


for page_type in page_types:

    results = collection.get(
        where={"page_type": page_type},
        include=["metadatas"]
    )

    print(f"\nPage type: {page_type}")
    print("Number of chunks:", len(results["ids"]))

    if len(results["metadatas"]) > 0:

        metadata = results["metadatas"][0]

        print("Sample metadata:")

        print("  page_number:",
              metadata.get("page_number"))

        print("  page_type:",
              metadata.get("page_type"))

        print("  text_source:",
              metadata.get("text_source"))

        print("  has_images:",
              metadata.get("has_images"))

        print("  image_count:",
              metadata.get("image_count"))

        print("  drawing_count:",
              metadata.get("drawing_count"))