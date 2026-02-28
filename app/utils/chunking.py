import tiktoken
from typing import List
from app.core.config import settings

def chunk_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
    """
    Split text into chunks based on token count using tiktoken.
    """
    if chunk_size is None:
        chunk_size = settings.chunk_size
    if chunk_overlap is None:
        chunk_overlap = settings.chunk_overlap
        
    encoding = tiktoken.get_encoding("cl100k_base") # encoding for text-embedding-3-small
    tokens = encoding.encode(text)
    
    chunks = []
    if len(tokens) == 0:
        return chunks
        
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        
        # Move start forward but account for overlap
        start += chunk_size - chunk_overlap
        
    return chunks
