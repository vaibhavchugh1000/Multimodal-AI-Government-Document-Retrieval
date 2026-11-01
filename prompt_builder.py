# prompt_builder.py module


def build_prompt(query, retrieved_documents, language):
    """
    Build the prompt for the LLM using the user's query
    and the retrieved government document chunks.

    Returns:
        str: Prompt to be sent to the LLM.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not retrieved_documents:
        raise ValueError("No retrieved documents available.")

    language_names = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "bn": "Bengali",
        "mr": "Marathi",
        "gu": "Gujarati",
        "kn": "Kannada",
        "ml": "Malayalam",
        "pa": "Punjabi",
        "ur": "Urdu",
        "or": "Odia",
        "as": "Assamese",
    }

    response_language = language_names.get(language, language)
    context_parts = []

    for index, document in enumerate(retrieved_documents, start=1):
        text = document["text"]
        metadata = document["metadata"]

        document_name = metadata.get(
            "document_name",
            "Unknown document"
        )

        page_number = metadata.get("page_number")
        paragraph_number = metadata.get("paragraph_number")

        if page_number is not None:
            source = f"{document_name}, Page {page_number}"
        elif paragraph_number is not None:
            source = f"{document_name}, Paragraph {paragraph_number}"
        else:
            source = document_name

        evidence_id = document.get(
            "evidence_id",
            f"E{index:03d}"
        )

        context_parts.append(
            f"[Evidence ID: {evidence_id}]\n"
            f"[Source: {source}]\n"
            f"[Chunk ID: {document.get('chunk_id', 'Unknown')}]\n"
            f"{text}"
        )
        
        print("distance of chunk ",index,"from query embedding = ",document["distance"])
        print("chunk id of chunk ",index," = ",document["chunk_id"])
        print("evidence id of chunk ",index," = ",document["evidence_id"])
        
            
            
    context = "\n\n".join(context_parts)

    prompt = f"""
You are a Government Document Assistant.

GENERAL INSTRUCTIONS:
1. Answer the user's specific question directly. Do not provide unrelated information.
2. Use only information supported by the provided government document context.
3. Do not invent facts, figures, or missing information.
4. If the required information is unavailable in the context, clearly state that it was not found in the available government documents.
5. If the context does not contain enough information, clearly explain this limitation.
6. Answer in {response_language}.
7. Do not make unsupported predictions.

NUMERICAL AND CALCULATION INSTRUCTIONS:
1. When the question asks for a calculation, comparison, difference, total, average, or percentage change, perform the required calculation using the retrieved values.
2. For every calculation, explicitly show the complete arithmetic expression using both the original values and the calculated result.

   For example:
   9.1 - 8.5 = 0.6

   Never display only the final input value as the calculation.
3. Never leave an equation incomplete or omit an operand.
4. Verify the arithmetic before presenting the answer.
5. Clearly mention the appropriate units.
6. When subtracting two percentages, express the difference in percentage points, not as a percentage, unless the question specifically asks for percentage change.
7. If a required input value is missing, do not assume or fabricate it. Explain which calculation cannot be completed.
8. For questions involving multiple indicators or time periods, address each requested indicator separately. Do not omit any requested comparison.
9. After presenting a comparison table, ensure that the calculations section independently shows the complete arithmetic for every indicator.

FORMATTING INSTRUCTIONS:
1. Use clear headings and bullet points where appropriate.
2. Present comparisons in a table when multiple indicators or periods are involved.
3. Use simple Markdown formatting for ordinary calculations. Use LaTeX delimiters only when mathematical notation genuinely requires them.
4. Keep the response clear, concise, and directly relevant.
5. Use LaTeX text commands such as \\text{{}} when necessary within mathematical expressions, but avoid unnecessary LaTeX formatting for ordinary text.
6. Place explanatory labels and descriptions outside mathematical expressions.
7. Do not include unnecessary backslashes or line-break commands inside mathematical delimiters.
8. Do not use trailing backslashes for line breaks. Use normal Markdown line breaks, headings, or bullet points.

RETRIEVED CONTEXT RELEVANCE INSTRUCTIONS:
1. Examine every retrieved evidence chunk independently before
   generating the answer.

2. Determine whether each chunk is directly relevant to the
   user's latest question.

3. Use only chunks that contain information directly relevant
   to answering the question.

4. Ignore irrelevant chunks, even if they contain information
   about the same broad subject or keywords as the question.

5. Do not force information from every retrieved chunk into
   the answer.

6. Do not cite irrelevant chunks as supporting evidence.

7. If a chunk contains both relevant and irrelevant information, 
extract only the relevant information. Do not use unrelated information from that 
chunk to expand the answer or support additional findings.

8. If only some aspects of the question are supported by the
   relevant chunks, answer those aspects and clearly identify
   what could not be established from the available context.

9. Base Key Findings and their Evidence IDs exclusively on
   the chunks actually used to support each finding.

User's Latest Question:
{query}

Detected Language:
{response_language}

Government Document Context:
{context}

STRUCTURED JSON OUTPUT INSTRUCTIONS:

Return the response strictly as a valid JSON object.
Do not include Markdown code fences or explanatory text outside the JSON.

Use the following structure:

{{
  "response_language": "{response_language}",

  "direct_answer": {{
    "text": "Answer the user's question in 2–3 concise sentences. Summarize the main conclusion without repeating the individual Key Findings."
  }},

  "key_findings": [
    {{
      "text": "First important finding.",
      "evidence_ids": ["E001", "E002"]
    }},
    {{
      "text": "Second important finding.",
      "evidence_ids": ["E003"]
    }}
  ],

  "evidence_ids": ["E001", "E002", "E003"]
}}

JSON OUTPUT RULES:

1. Each Key Finding must include its own evidence_ids list containing only the Evidence IDs that directly support that finding.

2. Examine all retrieved evidence chunks before selecting Evidence IDs.

3. Ignore irrelevant chunks and do not cite them.

4. Do not automatically reuse E001 or any other Evidence ID for every finding.

5. Different findings may cite the same Evidence ID only when that evidence genuinely supports each finding.

6. Use multiple Evidence IDs when multiple chunks jointly support a finding.

7. Use only Evidence IDs explicitly provided in the retrieved context. Never invent, modify, or guess an Evidence ID.

8. The overall evidence_ids list must contain all unique Evidence IDs used in the Key Findings.

9. If no retrieved evidence supports a finding, do not present it as an established fact.

10. If no relevant evidence is available, return an empty evidence_ids list and clearly explain the limitation in direct_answer.

11. The response_language must be {response_language}.

12. Return valid JSON only. Escape special characters properly and do not include trailing commas.

Now generate the JSON response following all the instructions above.
"""
    return prompt.strip()
