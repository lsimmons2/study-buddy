import faiss
from typing import List, Optional
import numpy as np

class FAISSIndex:
    def __init__(self, dimension: int, use_gpu: bool = False):
        """
        Initialize FAISS index.
        :param dimension: Dimensionality of embeddings.
        :param use_gpu: Whether to use GPU for FAISS.
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance (Euclidean)
        self.ids = []  # List of IDs for added embeddings
        if use_gpu:
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)

    def add_embeddings(self, ids: List[str], embeddings: List[List[float]]):
        """
        Add embeddings to the FAISS index.
        :param ids: List of unique IDs for embeddings.
        :param embeddings: List of embedding vectors.
        """
        assert len(ids) == len(embeddings), "IDs and embeddings must have the same length."
        self.ids.extend(ids)
        embeddings_np = np.array(embeddings, dtype="float32")
        self.index.add(embeddings_np)

    def search(self, query_embedding: List[float], top_k: int = 5):
        """
        Search for nearest neighbors in the FAISS index.
        :param query_embedding: Query embedding vector.
        :param top_k: Number of nearest neighbors to return.
        :return: List of tuples (id, distance).
        """
        query_np = np.array([query_embedding], dtype="float32")
        distances, indices = self.index.search(query_np, top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.ids):  # Valid index
                results.append({"id": self.ids[idx], "distance": float(dist)})
        return results
