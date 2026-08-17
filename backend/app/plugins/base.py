from abc import ABC, abstractmethod
from typing import Any, List, Optional
from pydantic import BaseModel


class MediaMetadata(BaseModel):
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    cover_url: Optional[str] = None
    external_id: Optional[str] = None


class MetadataProvider(ABC):
    """Base class for metadata providers"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def supported_media_types(self) -> List[str]:
        pass

    @abstractmethod
    async def search(self, query: str, media_type: str) -> List[MediaMetadata]:
        pass

    @abstractmethod
    async def get_by_id(self, external_id: str) -> Optional[MediaMetadata]:
        pass


class FulfillmentResult(BaseModel):
    """Outcome of a media-manager operation (connection test, add, status)."""

    ok: bool
    # Downstream id (e.g. the arr book id), stored on the request so we can later
    # poll availability.
    external_ref: Optional[str] = None
    # Free-form status label from get_status(), e.g. "queued" / "available".
    status: Optional[str] = None
    message: Optional[str] = None


class MediaManager(ABC):
    """Base class for downstream media managers (Readarr/Radarr/etc.).

    Unlike MetadataProvider, one adapter instance is shared across many
    configured MediaManagerInstance rows, so every method takes the instance
    config explicitly and the adapter itself holds no per-instance state. `config`
    and `request` are duck-typed (kept ORM-agnostic on purpose) — see
    MediaManagerInstance and Request models for the attributes used.
    """

    @property
    @abstractmethod
    def service(self) -> str:
        """Key that selects this adapter, matching MediaManagerInstance.service."""

    @abstractmethod
    async def test_connection(self, config: Any) -> FulfillmentResult:
        """Verify the instance is reachable and the API key is valid."""

    @abstractmethod
    async def add(self, config: Any, request: Any) -> FulfillmentResult:
        """Add the requested item to this instance; return its downstream ref."""

    @abstractmethod
    async def get_status(self, config: Any, external_ref: str) -> FulfillmentResult:
        """Report whether the referenced item is downloaded/available yet."""
