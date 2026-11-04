from language_detector import detect_language
from retriever import retrieve_documents
from prompt_builder import build_prompt
from llm_engine import generate_response
from feedback_store import save_interaction


# Number of chunks retrieved for each user query.
RETRIEVAL_TOP_K = 10


def user_query_pipeline(query):
    """
    Run the complete user query pipeline.

    Pipeline:
        Query
        -> Language Detection
        -> Retrieval
        -> Prompt Construction
        -> LLM
        -> Evidence ID / Citation Mapping
        -> Interaction and Retrieved-Chunk Storage
        -> Return interaction ID and answer
    """

    # Step 1: Validate the query.
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    query = query.strip()

    # Step 2: Detect the language of the user's query.
    language = detect_language(query)

    # Step 3: Retrieve the most relevant document chunks.
    retrieved_documents = retrieve_documents(
        query,
        top_k=RETRIEVAL_TOP_K
    )

    # Step 4: Build the prompt using the retrieved chunks.
    prompt = build_prompt(
        query,
        retrieved_documents,
        language
    )

    # Step 5: Generate the structured LLM response.
    json_llm_response = generate_response(prompt)

    if not isinstance(json_llm_response, dict):
        raise ValueError("The LLM response must be a dictionary.")

    # Step 6: Map the Evidence IDs selected by the LLM
    # to the corresponding retrieved chunks.
    evidence_ids = json_llm_response.get("evidence_ids", [])

    retrieved_lookup = {
        doc["evidence_id"]: doc
        for doc in retrieved_documents
    }

    citations = {}

    for evidence_id in evidence_ids:
        doc = retrieved_lookup.get(evidence_id)

        if doc is not None:
            citations[evidence_id] = doc
        else:
            print("Warning: Evidence ID not found:", evidence_id)

    # Preserve the existing response structure.
    json_llm_response["citation_list"] = citations
    json_llm_response["query"] = query
    json_llm_response["language"] = language

    # Step 7: Identify chunks whose sources are actually included
    # in the citation list shown to the user.
    cited_chunk_ids = {
        doc["chunk_id"]
        for doc in citations.values()
    }

    # Prepare all retrieved chunks for database storage.
    # Their original retrieval order is preserved.
    retrieved_chunks_for_storage = []

    for doc in retrieved_documents:
        retrieved_chunks_for_storage.append({
            "chunk_id": doc["chunk_id"],
            "text": doc["text"],
            "distance": doc.get("distance"),
            "metadata": doc.get("metadata") or {},
            "is_cited": doc["chunk_id"] in cited_chunk_ids
        })

    # Step 8: Save the interaction and all retrieved chunks.
    # feedback_store assigns chunk_rank based on list order.
    interaction_id = save_interaction(
        question=query,
        answer=json_llm_response,
        retrieved_chunks=retrieved_chunks_for_storage,
        retrieval_top_k=RETRIEVAL_TOP_K
    )

    # Step 9: Return the database-generated ID separately
    # from the structured LLM response.
    return {
        "interaction_id": interaction_id,
        "result": json_llm_response
    }
