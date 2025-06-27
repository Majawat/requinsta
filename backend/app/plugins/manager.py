from typing import Dict, List
from app.plugins.base import MetadataProvider, MediaMetadata
from app.plugins.openlibrary import OpenLibraryProvider


class PluginManager:
    def __init__(self):
        self.providers: Dict[str, MetadataProvider] = {}
        self._register_default_plugins()

    def _register_default_plugins(self):
        """Register built-in plugins"""
        self.register_provider(OpenLibraryProvider())

    def register_provider(self, provider: MetadataProvider):
        """Register a metadata provider"""
        self.providers[provider.name] = provider

    def get_providers_for_media_type(self, media_type: str) -> List[MetadataProvider]:
        """Get all providers that support the given media type"""
        return [
            provider
            for provider in self.providers.values()
            if media_type in provider.supported_media_types
        ]

    async def search_metadata(
        self, query: str, media_type: str
    ) -> Dict[str, List[MediaMetadata]]:
        """Search for metadata across all compatible providers"""
        results = {}
        providers = self.get_providers_for_media_type(media_type)

        for provider in providers:
            try:
                provider_results = await provider.search(query, media_type)
                results[provider.name] = provider_results
            except Exception as e:
                print(f"Error searching {provider.name}: {e}")
                results[provider.name] = []

        return results


# Global plugin manager instance
plugin_manager = PluginManager()
