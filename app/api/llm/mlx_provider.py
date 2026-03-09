from typing import List, Dict

from app.api.llm.base import LLMProvider


class MLXProvider(LLMProvider):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("MLXProvider will be implemented later.")

    def generate(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError("MLXProvider is not implemented yet.")