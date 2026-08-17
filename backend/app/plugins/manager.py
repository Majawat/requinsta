import asyncio
from typing import Dict, List
from app.plugins.base import MetadataProvider, MediaMetadata
from app.plugins.descriptor import METADATA_PROVIDER
from app.plugins.discovery import discover


class PluginManager:
    def __init__(self):
        self.providers: Dict[str, MetadataProvider] = {}
        for d in discover():
            if d.plugin_type == METADATA_PROVIDER:
                self.register_provider(d.obj)

    def register_provider(self, provider: MetadataProvider):
        self.providers[provider.name] = provider

    def get_providers_for_media_type(self, media_type: str) -> List[MetadataProvider]:
        return [
            provider
            for provider in self.providers.values()
            if media_type in provider.supported_media_types
        ]

    async def search_metadata(
        self, query: str, media_type: str
    ) -> Dict[str, List[MediaMetadata]]:
        providers = self.get_providers_for_media_type(media_type)

        async def safe_search(provider: MetadataProvider):
            try:
                return provider.name, await provider.search(query, media_type)
            except Exception as e:
                print(f"Error searching {provider.name}: {e}")
                return provider.name, []

        pairs = await asyncio.gather(*[safe_search(p) for p in providers])
        return dict(pairs)


plugin_manager = PluginManager()
