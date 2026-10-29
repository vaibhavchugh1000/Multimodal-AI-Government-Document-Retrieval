from retriever import retrieve_documents


query = "Who was assigned the work of looking after the publicity of the Ministry of Railways, Communications, Electronics and IT?"


results = retrieve_documents(query, top_k=5)


print("\n========================================")
print("RETRIEVAL TEST")
print("========================================")


print("\nNumber of retrieved documents:", len(results))


for index, result in enumerate(results, start=1):

    print("\n----------------------------------------")
    print(f"RESULT {index}")
    print("----------------------------------------")

    print("Chunk ID:", result["chunk_id"])

    print("Distance:", result["distance"])

    print("\nText:")
    print(result["text"][:500])

    print("\nMetadata:")

    for key, value in result["metadata"].items():
        print(f"  {key}: {value}")