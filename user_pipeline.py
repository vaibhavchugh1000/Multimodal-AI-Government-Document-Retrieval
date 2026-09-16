from language_detector import detect_language
from retriever import retrieve_documents
from prompt_builder import build_prompt
from llm_engine import generate_response


def user_query_pipeline(query):
    """
    Run the complete user query pipeline.

    Pipeline:
        Query
        → Language Detection
        → Retrieval
        → Prompt Construction
        → LLM
        → Answer

    Args:
        query: User's question as a string.

    Returns:
        dict: Answer, detected language, and retrieved sources.
    """

    # Step 1: Validate the query
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    # Step 2: Detect the language of the user's query
    language = detect_language(query)

    # Step 3: Retrieve the most relevant document chunks
    retrieved_documents = retrieve_documents(
        query,
        top_k=5
    )

    # Step 4: Build the prompt using the query and
    # retrieved government document context
    prompt = build_prompt(
        query,
        retrieved_documents,
        language
    )

    # Step 5: Send the prompt to the LLM
    answer = generate_response(prompt)

    # Step 6: Return the complete result
    return {
        "query": query,
        "language": language,
        "answer": answer,
        "sources": retrieved_documents
    }