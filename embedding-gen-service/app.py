import json
import traceback
from fastapi import FastAPI, HTTPException
from typing_extensions import List, TypedDict
import requests
import os
from sentence_transformers import SentenceTransformer

app = FastAPI(
    title="Embedding generation service",
    description="Service for generating embeddings")
# model = SentenceTransformer("all-MiniLM-L6-v2")  # 384
# model = SentenceTransformer("all-MiniLM-L12-v2")  # 384
model = SentenceTransformer("all-distilroberta-v1") # 768
# model = SentenceTransformer("msmarco-distilbert-base-v4") # 768


class EmbeddingsGenerationRequest(TypedDict):
    sentences: List[str]


class EmbeddingsGenerationResponse(TypedDict):
    embeddings: List[List[float]]


@app.get("/ping")
def ping_pong():
    return "pongggggggggg"


@app.post("/generate-embeddings", response_model=EmbeddingsGenerationResponse)
def generate_embeddings(request: EmbeddingsGenerationRequest) -> EmbeddingsGenerationResponse:
    if "sentences" not in request:
        raise HTTPException(status_code=400, detail="Missing 'sentences' field in request")

    sentences = request["sentences"]
    if not isinstance(sentences, list):
        raise HTTPException(status_code=400, detail="'sentences' must be a list of strings")

    embeddings = model.encode(sentences).tolist()  # Convert to list for JSON serialization
    return {"embeddings": embeddings}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
