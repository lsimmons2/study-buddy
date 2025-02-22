import json
import traceback
from fastapi import FastAPI, HTTPException
from models import AddEmbeddingsRequest, SearchRequest, SearchResponse
import faiss
from faiss_utils import FAISSIndex
from typing import List, Optional, TypedDict
import os
import numpy as np
import sys
sys.stdout.reconfigure(line_buffering=True)

from transcript_service_client import TranscriptChunk, TranscriptDetailsRest
import transcript_service_client 
transcript_config = transcript_service_client.Configuration(host=os.getenv("TRANSCRIPT_SERVICE_URL"))
transcript_api_client = transcript_service_client.ApiClient(configuration=transcript_config)
transcript_api = transcript_service_client.DefaultApi(transcript_api_client)


import embedding_gen_service_client 
embedding_gen_client = embedding_gen_service_client.ApiClient(
    configuration=embedding_gen_service_client.Configuration(host=os.getenv("EMBEDDING_GEN_SERVICE_URL")))
embedding_gen_api = embedding_gen_service_client.DefaultApi(embedding_gen_client)



app = FastAPI(
    title="Index embedding service",
    description="Service for managing and querying embeddings using FAISS")


faiss_index: FAISSIndex = FAISSIndex(dimension=768)
index_ids_to_chunks_ids: List[str] = []

@app.on_event("startup")
async def on_startup():
    global faiss_index
    global index_ids_to_chunks_ids
    print("Initializing FAISS index...")
    index_and_mapping  = initialize_index()
    faiss_index, index_ids_to_chunks_ids  = index_and_mapping
    # SNIPPET - checking for dupes
    if len(index_ids_to_chunks_ids) != len(list(set(index_ids_to_chunks_ids))):
        raise Exception("There are dupes in mapping!")
    print("FAISS index ready.")


INDEX_DIR = "index_dumps/"
INDEX_FILE_PATH = os.path.join(INDEX_DIR, "index.faiss")
INDEX_ID_MAP_FILE_PATH = os.path.join(INDEX_DIR, "index_id_map.json")


print("**** we in embedding-index service!!!!!!!!!!!!")
def save_faiss_index(index, file_path=INDEX_FILE_PATH):
    """
    Save the FAISS index to disk.
    """
    if not os.path.exists(INDEX_DIR):
        print("Making index dir")
        os.makedirs(INDEX_DIR)
    print(f"Saving FAISS index to {file_path}...")
    faiss.write_index(index, file_path)
    print("FAISS index saved successfully.")


def load_faiss_index(file_path=INDEX_FILE_PATH):
    """
    Load the FAISS index from disk if it exists.
    """
    if os.path.exists(file_path):
        print(f"Loading FAISS index from {file_path}...")
        index = faiss.read_index(file_path)
        print(f"FAISS index loaded successfully. {index.ntotal} embeddings found.")
        return index
    else:
        print(f"No FAISS index found at {file_path}. Starting fresh.")
        return None


def load_index_id_map(file_path=INDEX_ID_MAP_FILE_PATH):
    """
    Load the FAISS index from disk if it exists.
    """
    if os.path.exists(file_path):
        print(f"Loading index map from {file_path}...")
        with open(file_path, "r") as f:
            mapping = json.load(f)
        print(f"FAISS index loaded successfully.")
        return mapping
    else:
        print(f"No mapping found at {file_path}. Starting fresh.")
        return None


def write_index_id_map(ids:List[str], file_path=INDEX_ID_MAP_FILE_PATH):
    if not os.path.exists(INDEX_DIR):
        print("Making index dir")
        os.makedirs(INDEX_DIR)
    print(f"Writing index map from {file_path}: {len(ids)} ids being written")
    with open(file_path, "w") as f:
        json.dump(ids, f)


def initialize_index():
    """
    Initialize the FAISS index. Load from disk if it exists; otherwise, seed it.
    """
    # Step 1: Try to load the FAISS index
    index = load_faiss_index()
    index_id_mapping = load_index_id_map()
    if index is not None and index_id_mapping is not None:
        return index, index_id_mapping

    # Step 2: If no index exists, seed the index
    print("Seeding FAISS index...")

    all_ids = []
    index = faiss.IndexFlatL2(768)  # Replace with the appropriate FAISS index type and dimension
    # Fetch all script metadata
    scripts = transcript_api.list_scripts_scripts_get()
    print("***scripts returned be:", scripts)
    for script_meta in scripts:
        script_id = script_meta.id
        print(f"Fetching details for script ID: {script_id}")

        # Fetch full transcript details
        script = transcript_api.fetch_script_by_id_scripts_id_get(script_id)

        chunk_texts = [c.text for c in script.chunks]
        print(f"Found {len(chunk_texts)} chunks in script ID: {script_id}")

        # embeddings = generate_embeddings(chunk_texts)
        print("about to hit embedding api!!!")
        embeddings = embedding_gen_api\
            .generate_embeddings_generate_embeddings_post({"sentences":chunk_texts}).embeddings
        # print("got emebddings!:", embeddings)
        ids: List[str] = [f"{script_id}-{i}" for i in range(len(chunk_texts))]
        index.add(np.array(embeddings, dtype=np.float32))
        all_ids = all_ids + ids

    # Step 3: Save the newly created index
    save_faiss_index(index)
    write_index_id_map(all_ids)
    return index, all_ids


@app.get("/ping", response_model=str)
def ping_pong():
    return "pong"


@app.post("/search", response_model=SearchResponse)
def search_embeddings(request: SearchRequest):
    """
    Search for nearest neighbors using a query embedding.
    """
    try:
        query_embedding = np.array(request.query_embedding, dtype=np.float32).reshape(1, -1)
        # TODO: this typing ignore
        results: Tuple[List[float], List[int]] = faiss_index.search(query_embedding, request.top_k)  # type: ignore
        distances, ids = results
        # print("ids of neighbors from faiss index: %s" % (ids))
        return {"results": [
            {"id": index_ids_to_chunks_ids[id], "distance":d}
            for id, d in zip(ids.flatten().tolist(), distances.flatten().tolist())]}
    # SNIPPET
    except Exception as e:
        print("um hola???: %s" % (e))
        traceback.print_exc()
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
