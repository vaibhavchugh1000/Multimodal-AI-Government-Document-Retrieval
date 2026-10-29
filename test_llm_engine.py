# test_llm_engine module

from retriever import retrieve_documents
from prompt_builder import build_prompt
from llm_engine import generate_response


query = (
    "Who was assigned the work of looking after the publicity "
    "of the Ministry of Railways, Communications, Electronics and IT?"
)


# --------------------------------------------------
# 1. Retrieve relevant documents
# --------------------------------------------------

retrieved_documents = retrieve_documents(
    query,
    top_k=5
)


# --------------------------------------------------
# 2. Build LLM prompt
# --------------------------------------------------

prompt = build_prompt(
    query,
    retrieved_documents,
    "en"
)

print("=================prompt=======================")
print()
print(prompt)
print()
print("===================================================")
# --------------------------------------------------
# 3. Generate response
# --------------------------------------------------

response = generate_response(prompt)


# --------------------------------------------------
# 4. Display result
# --------------------------------------------------

print("\n========================================")
print("LLM ENGINE TEST")
print("========================================")

print("\nUser Question:")
print(query)

print("\nGenerated Answer:")
print(response)