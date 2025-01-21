import requests
import pytest
import pprint

QA_SERVICE_URL = "http://localhost:8003"

def create_question_round(file_path):
    response = requests.post(
        f"{QA_SERVICE_URL}/question-rounds",
        json={
            "filePath": file_path
        }
    )
    response.raise_for_status()
    return response.json()


def test_create_question_round():
    question_round = create_question_round("video-notes.txt")
    print("question_round:")
    pprint.pprint(question_round)
