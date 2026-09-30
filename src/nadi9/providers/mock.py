from typing import Any
import json
import os
from .base import LLMProvider, TranscriptionProvider

class MockLLMProvider(LLMProvider):
    def __init__(self, fixtures_path: str):
        self.fixtures_path = fixtures_path
        self.history = []
        # load mock responses
        self.responses = {}
        resp_file = os.path.join(fixtures_path, "mock_llm_responses.json")
        if os.path.exists(resp_file):
            with open(resp_file, 'r') as f:
                self.responses = json.load(f)

    def _get_mock_response(self, prompt: str) -> str:
        # Simplistic matching for mock purposes
        for key, value in self.responses.items():
            if key in prompt:
                return value
        return '{"error": "No mock response found for this prompt"}'

    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.0) -> str:
        res = self._get_mock_response(prompt)
        self.history.append({"prompt": prompt, "response": res})
        return res

    def structured_generate(self, prompt: str, response_schema: Any, system_prompt: str = "") -> Any:
        res_str = self._get_mock_response(prompt)
        try:
            res_dict = json.loads(res_str)
            return response_schema(**res_dict)
        except json.JSONDecodeError:
            raise ValueError(f"Mock response is not valid JSON: {res_str}")

class MockTranscriptionProvider(TranscriptionProvider):
    def __init__(self, fixtures_path: str):
        self.fixtures_path = fixtures_path

    def transcribe(self, audio_path: str) -> str:
        basename = os.path.basename(audio_path)
        transcript_path = os.path.join(self.fixtures_path, "transcripts", f"{basename}.txt")
        if os.path.exists(transcript_path):
            with open(transcript_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "Mock transcript not found."
