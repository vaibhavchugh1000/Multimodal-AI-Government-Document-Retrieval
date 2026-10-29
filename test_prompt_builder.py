# test_prompt_builder module

from retriever import retrieve_documents
from prompt_builder import build_prompt


query = (
    "Who was assigned the work of looking after the publicity "
    "of the Ministry of Railways, Communications, Electronics and IT?"
)


retrieved_documents = retrieve_documents(
    query,
    top_k=5
)


prompt = build_prompt(
    query,
    retrieved_documents,
    "en"
)


print("\n========================================")
print("PROMPT BUILDER TEST")
print("========================================")

print(prompt)