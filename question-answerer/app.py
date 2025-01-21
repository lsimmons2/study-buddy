import base64
from fastapi import FastAPI, HTTPException
from typing_extensions import List, TypedDict, Optional, Tuple
import json
import os

from ollama_client import prompt_ollama

from notes_service_client import FileQuestionsResponse, FileQuestion
import notes_service_client
notes_client = notes_service_client.ApiClient(
    configuration=notes_service_client.Configuration(host=os.getenv("NOTES_SERVICE_URL")))
notes_api = notes_service_client.DefaultApi(notes_client)

import embedding_index_service_client 
embedding_index_client = embedding_index_service_client.ApiClient(
    configuration=embedding_index_service_client.Configuration(host=os.getenv("EMBEDDING_INDEX_SERVICE_URL")))
embedding_index_api = embedding_index_service_client.DefaultApi(embedding_index_client)

import embedding_gen_service_client 
embedding_gen_client = embedding_gen_service_client.ApiClient(
    configuration=embedding_gen_service_client.Configuration(
        host=os.getenv("EMBEDDING_GEN_SERVICE_URL")))
embedding_gen_api = embedding_gen_service_client.DefaultApi(embedding_gen_client)


from transcript_service_client import TranscriptChunk
import transcript_service_client 
transcript_config = transcript_service_client.Configuration(host=os.getenv("TRANSCRIPT_SERVICE_URL"))
transcript_api_client = transcript_service_client.ApiClient(configuration=transcript_config)
transcript_api = transcript_service_client.DefaultApi(transcript_api_client)



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


app = FastAPI(
    title="Question answerer service",
    description="Service for attempting to elucidate questions user might have in their notes")



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
    question_embedding = embedding_gen_api\
            .generate_embeddings_generate_embeddings_post({"sentences":[question]}).embeddings[0]
    # question_embedding = generate_embeddings([question])[0]
    # nearest_neighbors = search_similar_chunks(question_embedding)["results"]
    search_req = {"query_embedding": question_embedding}
    nearest_neighbors = embedding_index_api.search_embeddings_search_post(search_req).results
    nearest_neighbor_chunks = [transcript_api.fetch_chunk_by_id_chunks_id_get(c.id) for c in nearest_neighbors]
    prompt = generate_rag_prompt(question, [c.text for c in nearest_neighbor_chunks])
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
    encoded_path = base64.b64encode(file_path.encode("utf-8")).decode("utf-8")
    questions_resp: FileQuestionsResponse = notes_api.get_file_questions_questions_get(encoded_path)
    questions: List[FileQuestion] = questions_resp.questions
    qa_attempts = [attempt_qa_with_rag(q.text) for q in questions]
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
