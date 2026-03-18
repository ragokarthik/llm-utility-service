from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic, List

T = TypeVar('T')


class Repository(ABC, Generic[T]):
    """Interface for repository pattern implementation."""

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get an entity by its ID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def update(self, id: str, entity: T) -> Optional[T]:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete an entity by ID."""
        pass
