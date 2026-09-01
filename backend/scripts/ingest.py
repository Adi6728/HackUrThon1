import os
import sys
import argparse

# Add backend to path so we can import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.document_ingestion.loader import load_document
from services.document_ingestion.chunker import chunk_documents
from services.document_ingestion.embedder import Embedder
from services.document_ingestion.vector_store import VectorStore

def ingest_document(file_path: str, ticker: str, persist_dir: str = "./data/chroma_db"):
    """Ingests a document into the vector store."""
    print(f"Starting ingestion for {file_path} (Ticker: {ticker})")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return
        
    # 1. Load
    docs = load_document(file_path, ticker)
    if not docs:
        print("No content loaded. Exiting.")
        return
    print(f"Loaded {len(docs)} pages/sections.")
    
    # 2. Chunk
    chunked_docs = chunk_documents(docs)
    print(f"Created {len(chunked_docs)} chunks.")
    
    # 3. Embed
    embedder = Embedder()
    texts_to_embed = [doc["text"] for doc in chunked_docs]
    embeddings = embedder.embed_texts(texts_to_embed)
    print(f"Generated {len(embeddings)} embeddings.")
    
    # 4. Store
    vector_store = VectorStore(persist_directory=persist_dir)
    vector_store.upsert_documents(chunked_docs, embeddings)
    print("Ingestion complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into ChromaDB.")
    parser.add_argument("file_path", help="Path to the document (PDF/TXT)")
    parser.add_argument("ticker", help="Stock ticker associated with the document")
    parser.add_argument("--db_path", default="./data/chroma_db", help="Path to persist ChromaDB")
    
    args = parser.parse_args()
    ingest_document(args.file_path, args.ticker, args.db_path)
