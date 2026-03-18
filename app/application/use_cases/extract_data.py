from typing import Optional, Dict, Any
from app.domain.entities.extraction import ExtractionResult
from app.domain.interfaces.llm_provider import LLMProvider


class ExtractDataUseCase:
    """Use case for extracting data from documents using LLM."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def execute(
        self,
        document_content: str,
        extraction_schema: Dict[str, Any],
        document_id: str
    ) -> ExtractionResult:
        """
        Execute the data extraction process.

        Args:
            document_content: The content of the document to extract data from.
            extraction_schema: The schema defining what data to extract.
            document_id: Unique identifier for the document.

        Returns:
            ExtractionResult containing the extracted data and metadata.
        """
        try:
            # Build the extraction prompt
            prompt = self._build_extraction_prompt(document_content, extraction_schema)

            # Use LLM to extract structured data
            extracted_data = await self.llm_provider.extract_structured_data(
                prompt=prompt,
                schema=extraction_schema
            )

            # Calculate confidence score (this would be more sophisticated in production)
            confidence_score = self._calculate_confidence(extracted_data, extraction_schema)

            # Create and return the result
            result = ExtractionResult(
                document_id=document_id,
                extracted_data=extracted_data,
                confidence_score=confidence_score,
                status="completed"
            )

            return result

        except Exception as e:
            # Return failed result
            result = ExtractionResult(
                document_id=document_id,
                extracted_data={},
                confidence_score=0.0,
                status="failed",
                error_message=str(e)
            )
            return result

    def _build_extraction_prompt(self, document_content: str, schema: Dict[str, Any]) -> str:
        """Build the prompt for data extraction."""
        return f"""
        Extract the following data from the document content below.
        
        Schema to extract: {schema}
        
        Document Content:
        {document_content}
        
        Return only the extracted data in JSON format matching the schema.
        """

    def _calculate_confidence(self, extracted_data: Dict[str, Any], schema: Dict[str, Any]) -> float:
        """
        Calculate confidence score for the extraction.
        This is a simplified implementation - in production, this would be more sophisticated.
        """
        if not extracted_data:
            return 0.0

        # Simple heuristic: ratio of filled fields to total fields
        schema_fields = len(schema.get("properties", {}))
        if schema_fields == 0:
            return 1.0

        filled_fields = len([v for v in extracted_data.values() if v is not None])
        return min(1.0, filled_fields / schema_fields)
