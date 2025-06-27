from abc import ABC, abstractmethod
from typing import Dict, List, Optional
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
