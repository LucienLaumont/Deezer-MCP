import httpx

DEEZER_API_BASE_URL = "https://api.deezer.com"


class DeezerClient:
    """Client HTTP minimal vers l'API publique Deezer (voir docs/deezer-api.md)."""

    def __init__(self, base_url: str = DEEZER_API_BASE_URL) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=10.0)

    async def close(self) -> None:
        await self._client.aclose()

    # Les méthodes (search, get_track, ...) seront ajoutées ensemble
    # au fur et à mesure qu'on construit les tools.
