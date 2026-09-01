from typing import List, Dict

def recursive_character_split(text: str, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[str]:
    """Splits text into chunks of chunk_size with chunk_overlap."""
    # A simple implementation of recursive character text splitting
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        
        # If we are not at the end, try to find a natural break (newline or period)
        if end < text_len:
            # Look back for a period or newline to split cleanly
            lookback_end = max(start, end - chunk_overlap * 2) # don't look back forever
            
            last_newline = text.rfind('\n', lookback_end, end)
            last_period = text.rfind('. ', lookback_end, end)
            
            if last_newline != -1:
                end = last_newline + 1 # Include the newline
            elif last_period != -1:
                end = last_period + 2 # Include the period and space
                
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        start = end - chunk_overlap
        if start < 0:
            start = 0
            
    return chunks

def chunk_documents(documents: List[Dict], chunk_size: int = 1000, chunk_overlap: int = 100) -> List[Dict]:
    """Chunks a list of loaded documents."""
    chunked_docs = []
    for doc in documents:
        text = doc["text"]
        metadata = doc["metadata"]
        
        chunks = recursive_character_split(text, chunk_size, chunk_overlap)
        
        for i, chunk in enumerate(chunks):
            chunk_meta = metadata.copy()
            chunk_meta["chunk_id"] = i
            
            chunked_docs.append({
                "text": chunk,
                "metadata": chunk_meta
            })
            
    return chunked_docs
