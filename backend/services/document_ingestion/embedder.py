from typing import List
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class Embedder:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        if SentenceTransformer is None:
            print("Warning: sentence_transformers not installed. Embeddings will not be generated locally.")
            return
            
        try:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print("Embedding model loaded.")
        except Exception as e:
            print(f"Error loading embedding model {self.model_name}: {e}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of texts."""
        if not self.model:
            raise ValueError("Embedding model not initialized.")
            
        if not texts:
            return []
            
        # Encode returns a numpy array, convert to list of floats for ChromaDB
        embeddings_array = self.model.encode(texts)
        return [embedding.tolist() for embedding in embeddings_array]
        
    def embed_query(self, query: str) -> List[float]:
        """Generates embedding for a single query string."""
        if not self.model:
            raise ValueError("Embedding model not initialized.")
            
        embedding = self.model.encode(query)
        return embedding.tolist()
