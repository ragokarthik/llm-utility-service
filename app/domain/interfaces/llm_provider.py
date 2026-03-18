from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Interface for LLM providers."""

    @abstractmethod
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate a completion based on the given prompt."""
        pass

    @abstractmethod
    async def extract_structured_data(self, prompt: str, schema: dict) -> dict:
        """Extract structured data based on the prompt and schema."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the LLM provider is available."""
        pass
