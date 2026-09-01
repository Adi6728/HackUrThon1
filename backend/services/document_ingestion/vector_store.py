import os
from typing import List, Dict, Optional
import uuid

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

class VectorStore:
    def __init__(self, persist_directory: str = "./data/chroma_db", collection_name: str = "financial_docs"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._initialize_db()

    def _initialize_db(self):
        if chromadb is None:
             print("Warning: chromadb not installed. Vector store will not function.")
             return
             
        os.makedirs(self.persist_directory, exist_ok=True)
        
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"} # Use cosine similarity
            )
            print(f"ChromaDB initialized at {self.persist_directory}, collection: {self.collection_name}")
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")

    def upsert_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        """Upserts documents and their embeddings into ChromaDB."""
        if not self.collection:
            raise ValueError("ChromaDB collection not initialized.")
            
        if not documents:
            return
            
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings.")
            
        ids = [str(uuid.uuid4()) for _ in range(len(documents))]
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        print(f"Upserted {len(documents)} documents to vector store.")

    def search(self, query_embedding: List[float], ticker: str, top_k: int = 3) -> List[Dict]:
        """Searches for similar documents filtered by ticker."""
        if not self.collection:
             print("Vector store not initialized, returning empty results.")
             return []
             
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"ticker": ticker}
        )
        
        docs = []
        if results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                docs.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "score": results['distances'][0][i] if 'distances' in results else None
                })
        return docs
