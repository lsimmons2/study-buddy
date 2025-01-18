from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
# model = SentenceTransformer("all-MiniLM-L6-v2")  # 384
# model = SentenceTransformer("all-MiniLM-L12-v2")  # 384
model = SentenceTransformer("all-distilroberta-v1") # 768
# model = SentenceTransformer("msmarco-distilbert-base-v4") # 768



@app.route("/ping", methods=["GET"])
def ping_pong():
    return "pong"


@app.route("/generate-embeddings", methods=["POST"])
def generate_embeddings():
    """
    Endpoint to generate embeddings for input sentences.
    Expects JSON with a "sentences" field: {"sentences": ["sentence1", "sentence2"]}
    Returns JSON with embeddings: {"embeddings": [[...], [...]]}
    """
    data = request.get_json()
    if "sentences" not in data:
        return jsonify({"error": "Missing 'sentences' field in request"}), 400

    sentences = data["sentences"]
    if not isinstance(sentences, list):
        return jsonify({"error": "'sentences' must be a list of strings"}), 400

    # Generate embeddings
    embeddings = model.encode(sentences).tolist()  # Convert to list for JSON serialization
    return jsonify({"embeddings": embeddings})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Expose the service on port 5000
