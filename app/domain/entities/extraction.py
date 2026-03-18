from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class ExtractionResult(BaseModel):
    """Entity representing the result of data extraction from a document."""
    
    id: Optional[str] = None
    document_id: str
    extracted_data: dict[str, Any]
    confidence_score: float = Field(ge=0.0, le=1.0)
    status: str = "pending"  # pending, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123",
                "extracted_data": {"field1": "value1", "field2": "value2"},
                "confidence_score": 0.95,
                "status": "completed"
            }
        }
