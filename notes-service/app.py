from fastapi import FastAPI, HTTPException
from typing_extensions import List, TypedDict, Optional, Tuple
import json
import base64
import os
import binascii
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Notes service",
    description="Service for dealing with user's notes files. ATOW just for parsing questions out of notes files.")


def parse_single_star_lines(file_path: str) -> list[Tuple[int, str]]:
    """
    Parses a .txt file and returns lines where the first non-whitespace character
    is a single '*' character. Skips lines where multiple contiguous '*' appear.

    Args:
        file_path (str): The path to the .txt file.

    Returns:
        list[str]: A list of lines matching the criteria.
    """
    result = []
    with open(file_path, "r") as file:
        for i, line in enumerate(file):
            stripped_line = line.lstrip()  # Remove leading whitespace
            if stripped_line.startswith("*") and not stripped_line.startswith("**"):
                result.append((i, line.strip()))
    return result

class FileQuestion(TypedDict):
    text: str
    line_index: int


class FileQuestionsResponse(TypedDict):
    file_path: str
    questions: List[FileQuestion]


@app.get("/ping")
def ping_pong():
    return "pong"


@app.get("/questions")
async def get_file_questions(file_path: str) -> FileQuestionsResponse:
    try:
        decoded_path = base64.b64decode(file_path).decode("utf-8")
        full_path = os.path.join("/notes/", decoded_path)
        
        if not os.path.exists(full_path):
            logger.error(f"File don't exist: {full_path}")
            raise HTTPException(status_code=400, detail="File does not exist")
        starred_lines = parse_single_star_lines(full_path)
        return {
            "file_path": full_path,
            "questions": [{"text": l[1], "line_index": l[0]} for l in starred_lines]
        }
    except (binascii.Error, UnicodeDecodeError) as e:
        logger.error(f"Failed to decode Base64 file path: {file_path}. Error: {e}")
        raise HTTPException(status_code=400, detail="Invalid Base64-encoded file path")
