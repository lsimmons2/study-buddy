from fastapi import FastAPI, HTTPException
from models import AddEmbeddingsRequest, SearchRequest, SearchResponse
from faiss_utils import FAISSIndex
from typing import List, Optional
import requests

app = FastAPI(title="Index embedding service", description="Service for managing and querying embeddings using FAISS")

faiss_index = FAISSIndex(dimension=768)


def fetch_data() -> List[dict]:
    """
    Simulate fetching data from a source. Replace this with actual logic to pull data from a database or API.
    """
    return [
        {"id": "1", "text": "This is the first document."},
        {"id": "2", "text": "Here is another document."},
    ]


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Call the embedding service to generate embeddings for the given texts.
    """
    response = requests.post(
        "http://greta:5000/generate-embeddings",
        json={"sentences": texts},
    )
    response.raise_for_status()
    return response.json()["embeddings"]


def seed_faiss_index():
    """
    Fetch data, generate embeddings, and seed the FAISS index.
    """
    try:
        # Fetch data
        data = fetch_data()
        ids = [item["id"] for item in data]
        texts = [item["text"] for item in data]

        # Generate embeddings
        embeddings = generate_embeddings(texts)

        # Add embeddings to the FAISS index
        faiss_index.add_embeddings(ids, embeddings)
        print(f"FAISS index seeded with {len(ids)} embeddings.")
    except Exception as e:
        print(f"Error during seeding: {str(e)}")
        raise

@app.on_event("startup")
async def on_startup():
    """
    Startup event to seed the FAISS index before the application starts serving requests.
    """
    print("Seeding FAISS index...")
    seed_faiss_index()
    print("Seeding completed.")

@app.get("/ping", response_model=str)
def ping_pong():
    return "pong"

@app.post("/add-embeddings", response_model=dict)
def add_embeddings(request: AddEmbeddingsRequest):
    """
    Add embeddings to the FAISS index.
    """
    print("hola in here")

    try:
        faiss_index.add_embeddings(request.ids, request.embeddings)
        return {"status": "success", "added": len(request.ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding embeddings: {str(e)}")

@app.post("/search", response_model=SearchResponse)
def search_embeddings(request: SearchRequest):
    """
    Search for nearest neighbors using a query embedding.
    """
    try:
        results = faiss_index.search(request.query_embedding, request.top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching embeddings: {str(e)}")


@app.get("/index-info", response_model=dict)
def index_info():
    """
    Returns information about the current state of the FAISS index.
    """
    try:
        # Get the number of vectors in the index
        vector_count = faiss_index.index.ntotal

        # Check if the index is trained
        is_trained = faiss_index.index.is_trained

        # Get the dimensionality of the vectors
        dimension = faiss_index.dimension

        # Return index information
        return {
            "status": "healthy",
            "index_trained": is_trained,
            "vector_count": vector_count,
            "dimension": dimension
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
