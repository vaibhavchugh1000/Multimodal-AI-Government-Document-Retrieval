# embedding_model module

from sentence_transformers import SentenceTransformer

model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

model=SentenceTransformer(model_name)

def create_embeddings(texts):
    
    if not texts:  
        raise ValueError("texts list cannot be empty")
    
    embeddings=model.encode(texts,convert_to_numpy=True,show_progress_bar=True)
    
    print("embeddings created successfully")
    print("Number of input texts:", len(texts))
    print("Number of embeddings:", len(embeddings))
    print("Embedding shape:", embeddings.shape)
    
    return embeddings