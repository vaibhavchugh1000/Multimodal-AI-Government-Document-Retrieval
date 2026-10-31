"""Paginated ChromaDB diagnostics for the Government Document RAG project.

Run from the project root:
    python check_vectors_count.py

The script reads the existing collection only; it does not modify stored data.
"""

from collections import Counter

from vector_store import collection


BATCH_SIZE = 500
EXPECTED_METADATA_FIELDS = [
    "document_id",
    "document_name",
    "document_path",
    "document_type",
    "text_source",
    "page_number",
    "page_type",
    "has_images",
    "image_count",
    "drawing_count",
]
EXPECTED_PAGE_TYPES = ("text", "image", "complex")


def inspect_collection():
    """Print collection size, document names, and multimodal integrity checks."""
    total_count = collection.count()

    print("\n========================================")
    print("CHROMADB STORAGE VERIFICATION")
    print("========================================")
    print("Total stored chunks:", total_count)

    if total_count == 0:
        print("The collection is empty; no metadata or embedding checks were run.")
        return

    document_names = set()
    page_type_counts = Counter()
    metadata_missing_counts = Counter()
    component_counts = Counter()
    first_chunk_text = None
    first_metadata = None
    first_embedding_dimension = None
    page_type_samples = {}

    # Fetch bounded batches rather than loading the entire vector collection
    # and all embeddings into memory at once.
    for offset in range(0, total_count, BATCH_SIZE):
        batch = collection.get(
            limit=BATCH_SIZE,
            offset=offset,
            include=["documents", "metadatas", "embeddings"],
        )

        ids = batch.get("ids") or []
        documents = batch.get("documents") or []
        metadatas = batch.get("metadatas") or []
        embeddings = batch.get("embeddings")
        embeddings = [] if embeddings is None else embeddings

        component_counts["ids"] += len(ids)
        component_counts["documents"] += len(documents)
        component_counts["metadatas"] += len(metadatas)
        component_counts["embeddings"] += len(embeddings)

        if first_chunk_text is None and documents:
            first_chunk_text = documents[0]
        if first_metadata is None and metadatas:
            first_metadata = metadatas[0]
        if first_embedding_dimension is None and embeddings:
            first_embedding_dimension = len(embeddings[0])

        for metadata in metadatas:
            metadata = metadata or {}
            name = metadata.get("document_name")
            if name:
                document_names.add(name)

            for field in EXPECTED_METADATA_FIELDS:
                if field not in metadata or metadata[field] is None:
                    metadata_missing_counts[field] += 1

            page_type = metadata.get("page_type")
            if page_type:
                page_type_counts[page_type] += 1
                page_type_samples.setdefault(page_type, metadata)

        # A short batch can indicate that the collection changed during the
        # scan or that the backend returned fewer records than requested.
        if not ids:
            break

    print("\nUnique document_names present in vector_db:")
    if document_names:
        for name in sorted(document_names):
            print(" -", name)
    else:
        print("No document_name metadata values were found.")

    print("\n========================================")
    print("SAMPLE STORED RECORD")
    print("========================================")
    if first_chunk_text is not None:
        print("First chunk text:")
        print(str(first_chunk_text)[:500])
    if first_metadata is not None:
        print("\nFirst chunk metadata:")
        for key, value in first_metadata.items():
            print(f"{key}: {value}")
    print("Embedding dimension:", first_embedding_dimension)

    print("\n========================================")
    print("COMPONENT COUNT CONSISTENCY")
    print("========================================")
    for component in ("ids", "documents", "embeddings", "metadatas"):
        print(f"{component.capitalize()}: {component_counts[component]}")

    counts_match = len({component_counts[key] for key in (
        "ids", "documents", "embeddings", "metadatas"
    )}) == 1
    if counts_match and component_counts["ids"] == total_count:
        print("All stored components have matching counts.")
    else:
        print("WARNING: Component counts do not match the collection count.")

    print("\n========================================")
    print("MULTIMODAL METADATA FIELD CHECK")
    print("========================================")
    for field in EXPECTED_METADATA_FIELDS:
        missing = metadata_missing_counts[field]
        if missing == 0:
            print(f"{field}: PRESENT in all scanned records")
        else:
            print(f"{field}: MISSING/NULL in {missing} scanned records")

    print("\n========================================")
    print("PAGE TYPE METADATA VERIFICATION")
    print("========================================")
    for page_type in EXPECTED_PAGE_TYPES:
        print(f"\nPage type: {page_type}")
        print("Number of chunks:", page_type_counts[page_type])
        metadata = page_type_samples.get(page_type)
        if metadata:
            for field in (
                "page_number",
                "page_type",
                "text_source",
                "has_images",
                "image_count",
                "drawing_count",
            ):
                print(f"  {field}: {metadata.get(field)}")
        else:
            print("  No records with this page_type were found.")

    unexpected_types = sorted(set(page_type_counts) - set(EXPECTED_PAGE_TYPES))
    if unexpected_types:
        print("Unexpected page_type values:", ", ".join(unexpected_types))

    print("\nDiagnostic scan complete. No ChromaDB records were modified.")


if __name__ == "__main__":
    inspect_collection()
