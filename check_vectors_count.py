from vector_store import collection

print("collection count = ",collection.count())
print()
document_names=set()

results=collection.get(include=["metadatas"])

for metadata in results["metadatas"]:
    
    document_names.add(metadata["document_name"])
    
print("unique document_names present in vector_db : ")
for name in document_names:
    print(name)