"""Multilingual embedding model used by the existing RAG pipeline."""

from sentence_transformers import SentenceTransformer

model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(model_name)


def create_embeddings(texts, batch_size=64, show_progress_bar=None):
    """Encode texts in configurable batches while retaining the existing model.

    Args:
        texts: Non-empty sequence of strings.
        batch_size: Number of texts processed per model batch.
        show_progress_bar: Explicit progress setting, or inferred for larger jobs.
    """
    if not texts:
        raise ValueError("texts list cannot be empty")
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")
    if any(not isinstance(text, str) for text in texts):
        raise TypeError("every item in texts must be a string")

    if show_progress_bar is None:
        show_progress_bar = len(texts) > batch_size

    embeddings = model.encode(
        list(texts),
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=show_progress_bar,
    )
    print("embeddings created successfully")
    return embeddings
