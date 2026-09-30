from abc import ABC, abstractmethod
from typing import Dict, Any, List

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.0) -> str:
        pass
        
    @abstractmethod
    def structured_generate(self, prompt: str, response_schema: Any, system_prompt: str = "") -> Any:
        pass

class TranscriptionProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        pass
