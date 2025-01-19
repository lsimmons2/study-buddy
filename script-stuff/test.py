import unittest
from typing import List, TypedDict
from app import break_script_into_chunks  # Import your function

# Define the required types
class TranscriptLine(TypedDict):
    timeStamp: int
    text: str

class Transcript(TypedDict):
    id: str
    name: str
    lines: List[TranscriptLine]

class TranscriptChunk(TypedDict):
    timeStamp: int
    text: str


class TestTranscriptChunking(unittest.TestCase):
    def setUp(self):
        """
        Set up fake test data for the tests.
        """
        # Example with sentences broken across multiple lines
        self.test_script = {
            "id": "test_id",
            "name": "Test Transcript",
            "lines": [
                {"timeStamp": 10, "text": "This is the first sentence. This is the second sentence,"},
                {"timeStamp": 20, "text": "which continues here. The third sentence starts here"},
                {"timeStamp": 30, "text": "and ends here."},
            ],
        }

        # Example with a single line and multiple sentences
        self.single_line_script = {
            "id": "test_id_2",
            "name": "Single Line Test Transcript",
            "lines": [
                {
                    "timeStamp": 15,
                    "text": "This is a single line with multiple sentences. Here's the second sentence. And finally, the third sentence."
                }
            ],
        }

    def test_chunking_with_multiple_lines(self):
        """
        Test chunking when sentences span across multiple lines.
        """
        expected_chunks = [
            {"timeStamp": 10, "text": "This is the first sentence."},
            {"timeStamp": 10, "text": "This is the second sentence, which continues here."},
            {"timeStamp": 20, "text": "The third sentence starts here and ends here."},
        ]

        chunks = break_script_into_chunks(self.test_script)
        print("chunks received: %s" % (chunks))
        self.assertEqual(chunks, expected_chunks)

    def test_chunking_with_single_line(self):
        """
        Test chunking when all sentences are within a single line.
        """
        expected_chunks = [
            {"timeStamp": 15, "text": "This is a single line with multiple sentences."},
            {"timeStamp": 15, "text": "Here's the second sentence."},
            {"timeStamp": 15, "text": "And finally, the third sentence."},
        ]

        chunks = break_script_into_chunks(self.single_line_script)
        self.assertEqual(chunks, expected_chunks)

    def test_empty_script(self):
        """
        Test chunking when the script is empty.
        """
        empty_script = {"id": "empty_id", "name": "Empty Transcript", "lines": []}
        expected_chunks = []

        chunks = break_script_into_chunks(empty_script)
        self.assertEqual(chunks, expected_chunks)

    def test_single_line_with_no_sentences(self):
        """
        Test chunking when a line has no sentences (just one block of text).
        """
        no_sentence_script = {
            "id": "test_id_3",
            "name": "No Sentences",
            "lines": [{"timeStamp": 5, "text": "This is a single line with no sentence boundaries"}],
        }
        expected_chunks = [
            {"timeStamp": 5, "text": "This is a single line with no sentence boundaries"}
        ]

        chunks = break_script_into_chunks(no_sentence_script)
        self.assertEqual(chunks, expected_chunks)


if __name__ == "__main__":
    unittest.main()
