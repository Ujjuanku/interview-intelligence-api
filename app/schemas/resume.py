from pydantic import BaseModel
from typing import List

class SearchChunk(BaseModel):
    text: str
    metadata: dict
    score: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchChunk]

class UploadResponse(BaseModel):
    filename: str
    num_chunks: int
    message: str
