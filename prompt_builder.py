
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
        "as": "Assamese"
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

        context_parts.append(
            f"[Source {index}: {source}]\n{text}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a Government Document Assistant.

Your task is to answer the user's latest question using
only the information available in the provided government
document context.

GENERAL INSTRUCTIONS:
1. Answer the specific question asked. Do not simply repeat
   an earlier answer or provide unrelated information.
2. Use only the provided document context.
3. Do not invent facts, figures, or missing information.
4. If the required information is unavailable in the context,
   clearly state that it was not found in the available
   government documents.
5. Answer in {response_language}.

NUMERICAL AND CALCULATION INSTRUCTIONS:
1. When the question asks for a calculation, comparison,
   difference, total, average, or percentage change, perform
   the required calculation using the retrieved values.
2. For every calculation, explicitly show the complete
   arithmetic expression using both the original values
   and the calculated result.

   For example:
   9.1 - 8.5 = 0.6

   Never display only the final input value as the
   calculation.
3. Never leave an equation incomplete or omit an operand.
4. Verify the arithmetic before presenting the answer.
5. Clearly mention the appropriate units.
6. When subtracting two percentages, express the difference
   in percentage points, not as a percentage, unless the
   question specifically asks for percentage change.
7. If a required input value is missing, do not assume or
   fabricate it. Explain which calculation cannot be completed.
8. For questions involving multiple indicators or time periods,
   address each requested indicator separately. Do not omit
   any requested comparison.
9. After presenting a comparison table, ensure that the
   calculations section independently shows the complete
   arithmetic for every indicator.   


FORMATTING INSTRUCTIONS:
1. Use clear headings and bullet points where appropriate.
2. Present comparisons in a table when multiple indicators
   or periods are involved.
3. Use simple Markdown formatting for ordinary calculations.
   Use LaTeX delimiters only when mathematical notation
   genuinely requires them.
4. Keep the response clear, concise, and directly relevant.
5. Use LaTeX text commands such as \\text{{}} when necessary
   within mathematical expressions, but avoid unnecessary
   LaTeX formatting for ordinary text.
6. Place explanatory labels and descriptions outside
   mathematical expressions.
7. Do not include unnecessary backslashes or line-break
   commands inside mathematical delimiters.
8. Do not use trailing backslashes for line breaks.
   Use normal Markdown line breaks, headings, or bullet points.

User's Latest Question:
{query}

Detected Language:
{response_language}

Government Document Context:
{context}

Now answer the user's latest question following all
the instructions above.
"""

    return prompt.strip()
