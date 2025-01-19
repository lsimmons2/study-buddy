import requests
import base64
from fastapi import FastAPI, HTTPException
from typing_extensions import List, TypedDict, Optional, Tuple
import json
import os


NOTES_SERVICE_URL = "http://notes-service:8002"
EMBEDDING_INDEX_URL = "http://embedding-index-service:8000"
EMBEDDING_GEN_SERVICE_URL = "http://192.168.1.155:5000"
TRANSCRIPT_SERVICE_URL = "http://transcript-service:8001"
OLLAMA_URL = "http://192.168.1.155:11434"

class TranscriptChunk(TypedDict):
    id: str
    timeStamp: int
    text: str


class CreateQuestionRoundRequest(TypedDict):
    filePath: str


class QaAttemptResponse(TypedDict):
    llmAnswer: str
    ragChunks: List[TranscriptChunk]
    questionText: str
    # questionLineIndex: int


class QuestionRoundResponse(TypedDict):
    filePath: str
    qaAttempts: List[QaAttemptResponse]


class FileQuestion(TypedDict):
    text: str
    line_index: int


class FileQuestionsResponse(TypedDict):
    file_path: str
    questions: List[FileQuestion]



app = FastAPI(
    title="Question answerer service",
    description="Service for attempting to elucidate questions user might have in their notes")


def get_file_questions(file_path: str) -> FileQuestionsResponse:
    encoded_path = base64.b64encode(file_path.encode("utf-8")).decode("utf-8")
    url = f"{NOTES_SERVICE_URL}/questions"
    response = requests.get(url, params={"file_path": encoded_path})
    return response.json()


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Call the embedding service to generate embeddings for the given texts.
    """
    response = requests.post(
        f"{EMBEDDING_GEN_SERVICE_URL}/generate-embeddings",
        json={"sentences": texts},
    )
    response.raise_for_status()
    return response.json()["embeddings"]


def search_similar_chunks(query_embedding, top_k=5):
    """
    Query the embedding index service to perform a similarity search.
    """
    response = requests.post(
        f"{EMBEDDING_INDEX_URL}/search",
        json={
            "query_embedding": query_embedding,
            "top_k": top_k
        }
    )
    response.raise_for_status()
    return response.json()


def fetch_chunk_by_id(script_id):
    response = requests.get(f"{TRANSCRIPT_SERVICE_URL}/chunks/{script_id}")
    response.raise_for_status()
    return response.json()


class OllamaResponse(TypedDict):
    model: str
    created_at: str
    response: str
    done: bool
    done_reason: str
    context: List[int]
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int


def prompt_ollama(prompt: str) -> OllamaResponse:
    data = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{OLLAMA_URL}/api/generate", json=data)
    response.raise_for_status()
    return response.json()


def generate_rag_prompt(question: str, chunks: List[str]) -> str:
    context = "\n\n".join(chunks)
    prompt = (
        "You are a helpful assistant. Use the following context to answer the question accurately:\n\n"
        f"{context.strip()}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )
    return prompt


class RagQaAttempt(TypedDict):
    question: str
    chunks_used: List[TranscriptChunk]
    answer: str


def attempt_qa_with_rag(question: str) -> RagQaAttempt:
    question_embedding = generate_embeddings([question])[0]
    nearest_neighbors = search_similar_chunks(question_embedding)["results"]
    nearest_neighbor_chunks = [fetch_chunk_by_id(c["id"]) for c in nearest_neighbors]
    prompt = generate_rag_prompt(question, [c["text"] for c in nearest_neighbor_chunks])
    ollama_resp = prompt_ollama(prompt)
    return {
        "question": question,
        "chunks_used": nearest_neighbor_chunks,
        "answer": ollama_resp["response"]
    }


@app.get("/ping")
def ping_pong():
    return "pong"


@app.post("/question-rounds", response_model=QuestionRoundResponse)
def new_question_round(body: CreateQuestionRoundRequest):
    file_path = body["filePath"]
    questions_resp: FileQuestionsResponse = get_file_questions(file_path)
    questions: List[FileQuestion] = questions_resp["questions"]
    qa_attempts = [attempt_qa_with_rag(q["text"]) for q in questions]
    print("got dem qa attempts: %s" % (qa_attempts))
    return {
        "filePath": file_path,
        "qaAttempts": [
            {
                "llmAnswer": a["answer"],
                "ragChunks": a["chunks_used"],
                "questionText": a["question"]
                }
            for a in qa_attempts
        ]
    }
