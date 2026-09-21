# text cleaner module

import re


def clean_records(records):
    """
    Clean the text in document records while preserving metadata.

    Returns:
        list: A list of cleaned document records.
    """

    cleaned_records = []

    for record in records:

        text = record["text"]

        text = re.sub(r"[ \t]+", " ", text)

        text = re.sub(r"\n\s*\n+", "\n\n", text)

        text = text.strip()

        if text:

            cleaned_record = record.copy()

            cleaned_record["text"] = text

            cleaned_records.append(cleaned_record)

    print("records cleaned successfully")
    return cleaned_records