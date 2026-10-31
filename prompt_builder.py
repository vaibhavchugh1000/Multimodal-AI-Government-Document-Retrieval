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

User's Latest Question:
{query}

Detected Language:
{response_language}

Government Document Context:
{context}

Structure your response using these sections:

1. Direct Answer:
   Answer the user's question first in 2–3 concise sentences.
   Summarize the main conclusion without repeating the
   individual points that will appear under Key Findings.

2. Key Findings:
   Present the main findings from the provided government
   document context as clear bullet points.

Citation rules:
- Each Key Finding must include the Evidence ID or IDs
  that directly support that specific finding.
- Examine all provided evidence chunks before selecting citations.
- Do not automatically reuse E001 or any other ID for every finding.
- Different findings may cite the same Evidence ID only when
  that evidence genuinely supports each finding.
- Use multiple Evidence IDs when multiple chunks jointly
  support a finding.
- Use only Evidence IDs explicitly provided in the context.
- Never invent, modify, or guess an Evidence ID.
- If no retrieved evidence supports a claim, do not present
  that claim as an established fact.
- Preserve the exact citation format, such as [E001] or [E003].

Now answer the user's latest question following all the instructions above.
"""

    return prompt.strip()
