from pydantic import BaseModel
from typing import List, Optional

class AddEmbeddingsRequest(BaseModel):
    ids: List[str]  # Unique IDs for embeddings
    embeddings: List[List[float]]  # List of embedding vectors

class SearchRequest(BaseModel):
    query_embedding: List[float]  # Query vector
    top_k: int = 5  # Number of nearest neighbors to return

# Define the structure of each result
class SearchResult(BaseModel):
    id: str  # ID of the nearest neighbor
    distance: float  # Distance (or similarity score)

# Define the response model
class SearchResponse(BaseModel):
    results: List[SearchResult]  # List of typed results
