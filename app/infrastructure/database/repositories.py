from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.interfaces.repository import Repository
from app.domain.entities.extraction import ExtractionResult
from app.infrastructure.database.models import ExtractionRecord


class ExtractionRepository(Repository[ExtractionResult]):
    """SQLAlchemy implementation of the extraction repository."""

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: str) -> Optional[ExtractionResult]:
        """Get an extraction result by its database ID."""
        record = self.db.query(ExtractionRecord).filter(ExtractionRecord.id == int(id)).first()
        if not record:
            return None
        return self._to_entity(record)

    async def get_by_document_id(self, document_id: str) -> Optional[ExtractionResult]:
        """Get an extraction result by document ID."""
        record = self.db.query(ExtractionRecord).filter(
            ExtractionRecord.document_id == document_id
        ).order_by(ExtractionRecord.created_at.desc()).first()
        if not record:
            return None
        return self._to_entity(record)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ExtractionResult]:
        """Get all extraction results with pagination."""
        records = self.db.query(ExtractionRecord).offset(skip).limit(limit).all()
        return [self._to_entity(record) for record in records]

    async def create(self, entity: ExtractionResult) -> ExtractionResult:
        """Create a new extraction result."""
        record = ExtractionRecord(
            document_id=entity.document_id,
            extracted_data=entity.extracted_data,
            confidence_score=entity.confidence_score,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            error_message=entity.error_message
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return self._to_entity(record)

    async def update(self, id: str, entity: ExtractionResult) -> Optional[ExtractionResult]:
        """Update an existing extraction result."""
        record = self.db.query(ExtractionRecord).filter(ExtractionRecord.id == int(id)).first()
        if not record:
            return None

        record.document_id = entity.document_id
        record.extracted_data = entity.extracted_data
        record.confidence_score = entity.confidence_score
        record.status = entity.status
        record.updated_at = entity.updated_at
        record.error_message = entity.error_message

        self.db.commit()
        self.db.refresh(record)
        return self._to_entity(record)

    async def delete(self, id: str) -> bool:
        """Delete an extraction result by ID."""
        record = self.db.query(ExtractionRecord).filter(ExtractionRecord.id == int(id)).first()
        if not record:
            return False

        self.db.delete(record)
        self.db.commit()
        return True

    def _to_entity(self, record: ExtractionRecord) -> ExtractionResult:
        """Convert database record to domain entity."""
        return ExtractionResult(
            id=str(record.id),
            document_id=record.document_id,
            extracted_data=record.extracted_data,
            confidence_score=record.confidence_score,
            status=record.status,
            created_at=record.created_at,
            updated_at=record.updated_at,
            error_message=record.error_message
        )
