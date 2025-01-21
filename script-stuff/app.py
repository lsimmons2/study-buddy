from fastapi import FastAPI, HTTPException
from typing_extensions import List, TypedDict, Optional, Tuple
import json
import os
import nltk
from nltk.tokenize import sent_tokenize
# nltk.download('punkt_tab')



SCRIPT_DB_FP = "/ai_transcripts/"

def generate_chunk_id(transcript_id: str, chunk_index: int) -> str:
    """
    Generate a unique chunk ID from the transcript ID and chunk index.
    """
    return f"{transcript_id}-{chunk_index}"


def parse_chunk_id(chunk_id: str) -> Tuple[str, int]:
    """
    Parse the chunk ID to retrieve the transcript ID and chunk index.
    """
    transcript_id, chunk_index = chunk_id.rsplit("-", 1)
    return transcript_id, int(chunk_index)

# SNIPPET - typed dicts
class TranscriptLine(TypedDict):
    timeStamp: int
    text: str


class Transcript(TypedDict):
    id: str
    name: str
    lines: List[TranscriptLine]


class TranscriptChunk(TypedDict):
    id: str
    timeStamp: int
    text: str


class TranscriptDetailsRest(TypedDict):
    id: str
    name: str
    chunks: List[TranscriptChunk]


class TranscriptSummaryRest(TypedDict):
    id: str
    name: str


def get_chunks_with_ids(script_id:str, almost_chunks: List[Tuple[int, str]]) -> List[TranscriptChunk]:
    return [
        {
            "id": generate_chunk_id(script_id, i),
            "text": c[1],
            "timeStamp": c[0]
        }
        for i, c in enumerate(almost_chunks)
    ]


def get_scripts() -> List[Transcript]:
    rv = []
    for file_name in os.listdir(SCRIPT_DB_FP):
        file_path = os.path.join(SCRIPT_DB_FP, file_name)
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                rv.append(data)
    return rv
    # return [s for s in rv if s["id"] == "PLSjqHtyw3E"]
    # return rv[:1]


def split_script_into_sentences(script: Transcript) -> list[str]:
    text = " ".join([l["text"] for l in script["lines"]])
    return sent_tokenize(text)


def break_script_into_chunks(script: Transcript) -> List[TranscriptChunk]:
    sentences = split_script_into_sentences(script)
    if len(sentences) == 1:
        line_chunks = [(l["timeStamp"], l["text"]) for l in script["lines"]]
        return get_chunks_with_ids(script["id"], line_chunks)

    # now break up into chunks, assigning the right timestamps
    lines = script["lines"]

    # Step 1: Create a concatenated string and track line indices
    concatenated_text = ""
    line_index_mapping = []  # List of (start_idx, end_idx, timestamp)

    current_idx = 0
    for line in lines:
        start_idx = current_idx
        concatenated_text += line["text"] + " "
        end_idx = current_idx + len(line["text"])
        line_index_mapping.append((start_idx, end_idx, line["timeStamp"]))
        current_idx = end_idx + 1  # Account for the added space

    # Step 3: Assign timestamps to each sentence
    chunks: List[Tuple[int, str]] = []
    for sentence in sentences:
        # Find the start index of the sentence in the concatenated text
        sentence_start_idx = concatenated_text.find(sentence)

        if sentence_start_idx == None:
            raise Exception("This shouldn't happen??")

        # Determine which line the sentence belongs to based on the index mapping
        for start_idx, end_idx, timestamp in line_index_mapping:
            if start_idx <= sentence_start_idx < end_idx:
                chunks.append((timestamp, sentence))
                break


    return get_chunks_with_ids(script["id"], chunks)


def get_script_by_id(video_id: str) -> Optional[Transcript]:
    scripts = get_scripts()
    return next((s for s in scripts if s["id"] == video_id), None)


def get_chunk_by_id(chunk_id: str) -> Optional[TranscriptChunk]:
    transcript_id, chunk_index = parse_chunk_id(chunk_id)
    script = get_script_by_id(transcript_id)
    if script is None:
        print("No such script found for chunk")
        return None
    chunks = break_script_into_chunks(script)
    c_ts = [c["text"] for c in chunks]
    # if len(c_ts) != len(list(set(c_ts))):
    #     print("there are dupes in these chunks!!!!!!")
    # else:
    #     print("there are no dupes in these chunks!!!!!!")
    chunk = chunks[chunk_index]
    return chunk


def peep_script_chunks(video_id: str):
    print("\n\n")
    script = get_script_by_id(video_id)
    if not script:
        print("no script")
        return
    chunks = break_script_into_chunks(script)
    print("script name: %s" % (script["name"]))
    print("nb chunks: %d" % (len(chunks)))
    print("first 5:")
    for c in chunks[:5]:
        print()
        print(c)


app = FastAPI(title="Transcript Service", description="Service for managing video transcripts")


@app.get("/ping")
def ping_pong():
    return "pong"

@app.get("/scripts", response_model=List[TranscriptSummaryRest])
def list_scripts():
    """
    Returns a list of metadata (id and name) for all available scripts.
    """
    scripts = get_scripts()
    return [{"id": script["id"], "name": script["name"]} for script in scripts]


@app.get("/scripts/{id}", response_model=TranscriptDetailsRest)
def fetch_script_by_id(id: str) -> TranscriptDetailsRest:
    """
    Returns the full transcript for a given script ID.
    """
    script = get_script_by_id(id)
    if script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    chunks = break_script_into_chunks(script)
    return {"id":script["id"], "name":script["name"], "chunks":chunks}


@app.get("/chunks/{id}", response_model=TranscriptChunk)
def fetch_chunk_by_id(id: str) -> TranscriptChunk:
    chunk = get_chunk_by_id(id)
    if chunk is None:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return chunk


if __name__ == "__main__":
    scripts = get_scripts()
    # print(scripts[0]["name"])
    # print(len(scripts[0]["lines"]))

    # The Fabric of Knowledge - David Spivak
    peep_script_chunks("ju17bM9p2RU")
    peep_script_chunks("xw7omaQ8SgA")
    peep_script_chunks("sw8IE3MX1SY")
