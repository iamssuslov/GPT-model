from abc import ABC, abstractmethod
from typing import List, Dict


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        """Generate a response from the model."""
        raise NotImplementedError