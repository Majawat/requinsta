from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.models import Base


class MediaManagerInstance(Base):
    """A configured downstream media-manager instance (Readarr/Radarr/Sonarr/
    Lidarr and Readarr-API-compatible forks like Bookshelf/Chaptarr).

    One row per instance so a user with, e.g., separate Readarr instances for
    ebooks vs audiobooks can register both and route requests to the right one.
    Rows are the source of truth the plugin layer loads at request time; with no
    rows configured, the app simply offers no automated fulfillment (manual
    workflow still works).
    """

    __tablename__ = "media_manager_instances"

    id = Column(Integer, primary_key=True, index=True)
    # Plugin key that selects the adapter, e.g. "readarr". Multiple instances may
    # share a service.
    service = Column(String, nullable=False)
    # Human label shown in the admin UI, e.g. "Readarr - Audiobooks".
    name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    api_key = Column(String, nullable=True)
    # Which MediaType values this instance can fulfill, e.g. ["book", "audiobook"].
    media_types = Column(JSON, nullable=False, default=list)
    enabled = Column(Boolean, nullable=False, default=True)

    # Arr add-time parameters. Nullable so an instance can be registered first and
    # completed once the admin has picked folders/profiles from the arr.
    root_folder_path = Column(String, nullable=True)
    quality_profile_id = Column(Integer, nullable=True)
    metadata_profile_id = Column(Integer, nullable=True)  # Readarr/Lidarr only

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
