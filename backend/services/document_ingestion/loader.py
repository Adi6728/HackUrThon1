import pymupdf  # PyMuPDF
from typing import List, Dict

def load_pdf(file_path: str, ticker: str) -> List[Dict]:
    """Loads a PDF document and extracts text page by page."""
    docs = []
    try:
        doc = pymupdf.open(file_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                docs.append({
                    "text": text,
                    "metadata": {
                        "source": file_path,
                        "page": page_num + 1,
                        "ticker": ticker
                    }
                })
        doc.close()
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    return docs

def load_text(file_path: str, ticker: str) -> List[Dict]:
    """Loads a text document."""
    docs = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            if text.strip():
                docs.append({
                    "text": text,
                    "metadata": {
                        "source": file_path,
                        "page": 1,
                        "ticker": ticker
                    }
                })
    except Exception as e:
         print(f"Error loading {file_path}: {e}")
    return docs

def load_document(file_path: str, ticker: str) -> List[Dict]:
    """Route document to appropriate loader based on extension."""
    if file_path.lower().endswith('.pdf'):
        return load_pdf(file_path, ticker)
    else:
        return load_text(file_path, ticker)
