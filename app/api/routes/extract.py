from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid

from app.application.use_cases.extract_data import ExtractDataUseCase
from app.infrastructure.llm.groq_client import GroqClient
from app.infrastructure.parsers.pdf_parser import PDFParser
from app.infrastructure.database.session import get_db
from app.infrastructure.database.repositories import ExtractionRepository
from app.domain.entities.extraction import ExtractionResult


router = APIRouter(prefix="/extract", tags=["extraction"])


def get_llm_provider() -> GroqClient:
    """Dependency to get LLM provider."""
    return GroqClient()


def get_pdf_parser() -> PDFParser:
    """Dependency to get PDF parser."""
    return PDFParser()


@router.post("/pdf", response_model=ExtractionResult)
async def extract_from_pdf(
    file: UploadFile = File(...),
    schema: Optional[str] = None,
    llm_provider: GroqClient = Depends(get_llm_provider),
    pdf_parser: PDFParser = Depends(get_pdf_parser),
    db: Session = Depends(get_db)
):
    """
    Extract data from a PDF document.

    Args:
        file: PDF file to extract data from.
        schema: JSON schema defining what data to extract (optional).
        llm_provider: LLM provider dependency.
        pdf_parser: PDF parser dependency.
        db: Database session dependency.

    Returns:
        ExtractionResult with the extracted data.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Default extraction schema
    default_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "date": {"type": "string"},
            "content": {"type": "string"}
        }
    }

    # Parse custom schema if provided
    if schema:
        import json
        try:
            extraction_schema = json.loads(schema)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON schema")
    else:
        extraction_schema = default_schema

    try:
        # Parse PDF content
        file_content = await file.read()
        from io import BytesIO
        pdf_content = await pdf_parser.parse(BytesIO(file_content))

        # Generate document ID
        document_id = str(uuid.uuid4())

        # Execute extraction use case
        use_case = ExtractDataUseCase(llm_provider=llm_provider)
        result = await use_case.execute(
            document_content=pdf_content,
            extraction_schema=extraction_schema,
            document_id=document_id
        )

        # Store result in database
        repository = ExtractionRepository(db=db)
        stored_result = await repository.create(result)

        return stored_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.get("/{extraction_id}", response_model=ExtractionResult)
async def get_extraction_result(
    extraction_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a previously extracted result by ID.

    Args:
        extraction_id: ID of the extraction result.
        db: Database session dependency.

    Returns:
        The extraction result.
    """
    repository = ExtractionRepository(db=db)
    result = await repository.get_by_id(extraction_id)

    if not result:
        raise HTTPException(status_code=404, detail="Extraction result not found")

    return result


@router.get("/document/{document_id}", response_model=ExtractionResult)
async def get_extraction_by_document_id(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get extraction result by document ID.

    Args:
        document_id: ID of the document.
        db: Database session dependency.

    Returns:
        The extraction result.
    """
    repository = ExtractionRepository(db=db)
    result = await repository.get_by_document_id(document_id)

    if not result:
        raise HTTPException(status_code=404, detail="Extraction result not found")

    return result
