from typing import List, TypedDict
import json
import os


SCRIPT_DB_FP = "/Users/leo/ai_transcripts/"



# SNIPPET - typed dicts
class TranscriptLine(TypedDict):
    timeStamp: int
    text: str


class Transcript(TypedDict):
    id: str
    name: str
    lines: List[TranscriptLine]


def get_scripts() -> List[Transcript]:
    rv = []
    for file_name in os.listdir(SCRIPT_DB_FP):
        file_path = os.path.join(SCRIPT_DB_FP, file_name)
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                rv.append(data)
    return rv


if __name__ == "__main__":
    scripts = get_scripts()
    print(scripts[0]["name"])
    print(len(scripts[0]["lines"]))



    

