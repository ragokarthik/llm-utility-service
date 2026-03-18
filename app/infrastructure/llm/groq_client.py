import os
from typing import Optional, Dict, Any
from app.domain.interfaces.llm_provider import LLMProvider


class GroqClient(LLMProvider):
    """Groq LLM provider implementation."""

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.1-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self._client = None

    @property
    def client(self):
        """Lazy initialization of the Groq client."""
        if self._client is None:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "groq package not installed. Install it with: pip install groq"
                )
        return self._client

    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate a completion based on the given prompt."""
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1024)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    async def extract_structured_data(self, prompt: str, schema: dict) -> dict:
        """Extract structured data based on the prompt and schema."""
        import json

        # Enhance prompt to request JSON output
        enhanced_prompt = f"""
        {prompt}
        
        IMPORTANT: Respond ONLY with valid JSON that matches this schema:
        {schema}
        
        Do not include any explanation or additional text. Only return the JSON object.
        """

        response_text = await self.generate_completion(
            enhanced_prompt,
            temperature=0.1  # Lower temperature for more deterministic output
        )

        # Parse the JSON response
        try:
            # Try to extract JSON from the response
            extracted_json = self._extract_json_from_response(response_text)
            return extracted_json
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from LLM response: {e}")

    def _extract_json_from_response(self, response_text: str) -> dict:
        """Extract JSON from LLM response text."""
        import json
        import re

        # Try to find JSON object in the response
        json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        # If no match, try to parse the entire response as JSON
        return json.loads(response_text.strip())

    async def is_available(self) -> bool:
        """Check if the LLM provider is available."""
        try:
            if not self.api_key:
                return False

            # Try a simple completion to check availability
            await self.generate_completion("Hello", max_tokens=5)
            return True
        except Exception:
            return False
