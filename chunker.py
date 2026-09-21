# chunker module

def chunk_records(records, chunk_size=1000, chunk_overlap=150):
    """
    Split document records into smaller overlapping chunks
    while preserving their metadata.

    Returns:
        list: A list of chunk records.
    """

    chunks = []

    for record in records:

        text = record["text"]

        start = 0
        text_length = len(text)

        while start < text_length:

            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:

                chunk = record.copy()

                chunk["text"] = chunk_text

                chunk["chunk_id"] = (
                    f"{record['document_id']}_chunk_"
                    f"{len(chunks) + 1:04d}"
                )

                chunks.append(chunk)

            start = end - chunk_overlap

    print("chunks created successfully")
    return chunks