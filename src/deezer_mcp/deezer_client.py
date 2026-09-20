import httpx

DEEZER_API_BASE_URL = "https://api.deezer.com"


class DeezerAPIError(Exception):
    """Erreur renvoyée par l'API Deezer (payload {"error": {...}}, toujours en HTTP 200)."""


class DeezerClient:
    """Client HTTP vers l'API publique Deezer (voir docs/deezer-api.md).

    Chaque méthode publique renvoie des dicts "propres" (champs utiles seulement),
    pas les objets bruts Deezer qui contiennent beaucoup de champs inutiles pour un modèle.
    """

    def __init__(self, base_url: str = DEEZER_API_BASE_URL) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=10.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str, params: dict | None = None) -> dict:
        try:
            response = await self._client.get(path, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise DeezerAPIError(f"Deezer a répondu {exc.response.status_code} pour {path}") from exc
        except httpx.RequestError as exc:
            raise DeezerAPIError(f"Impossible de contacter l'API Deezer ({path}): {exc}") from exc

        payload = response.json()
        if isinstance(payload, dict) and "error" in payload:
            message = payload["error"].get("message", "erreur inconnue")
            raise DeezerAPIError(f"Deezer: {message} (requête: {path})")
        return payload

    async def search_tracks(self, query: str, limit: int = 10) -> list[dict]:
        payload = await self._get("/search/track", {"q": query, "limit": limit})
        return [self._shape_track(item) for item in payload["data"]]

    async def search_albums(self, query: str, limit: int = 10) -> list[dict]:
        payload = await self._get("/search/album", {"q": query, "limit": limit})
        return [self._shape_album(item) for item in payload["data"]]

    async def search_artists(self, query: str, limit: int = 10) -> list[dict]:
        payload = await self._get("/search/artist", {"q": query, "limit": limit})
        return [self._shape_artist(item) for item in payload["data"]]

    async def get_track(self, track_id: int) -> dict:
        payload = await self._get(f"/track/{track_id}")
        return self._shape_track(payload)

    async def get_album(self, album_id: int) -> dict:
        payload = await self._get(f"/album/{album_id}")
        album = self._shape_album(payload)
        album["tracks"] = [self._shape_track(item) for item in payload.get("tracks", {}).get("data", [])]
        return album

    async def get_artist_top_tracks(self, artist_id: int, limit: int = 10) -> list[dict]:
        payload = await self._get(f"/artist/{artist_id}/top", {"limit": limit})
        return [self._shape_track(item) for item in payload["data"]]

    async def fetch_album_cover(self, album_id: int) -> bytes:
        album = await self._get(f"/album/{album_id}")
        cover_url = album.get("cover_medium")
        if not cover_url:
            raise DeezerAPIError(f"Pas de pochette disponible pour l'album {album_id}")
        return await self._fetch_binary(cover_url)

    async def fetch_artist_picture(self, artist_id: int) -> bytes:
        artist = await self._get(f"/artist/{artist_id}")
        picture_url = artist.get("picture_medium")
        if not picture_url:
            raise DeezerAPIError(f"Pas de photo disponible pour l'artiste {artist_id}")
        return await self._fetch_binary(picture_url)

    async def _fetch_binary(self, url: str) -> bytes:
        try:
            # URL absolue vers un autre hôte (cdn-images.dzcdn.net) que la base_url
            # de ce client (api.deezer.com) — httpx utilise l'URL absolue telle quelle.
            response = await self._client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise DeezerAPIError(f"Deezer a répondu {exc.response.status_code} pour {url}") from exc
        except httpx.RequestError as exc:
            raise DeezerAPIError(f"Impossible de télécharger {url}: {exc}") from exc
        return response.content

    @staticmethod
    def _shape_track(raw: dict) -> dict:
        artist = raw.get("artist") or {}
        album = raw.get("album") or {}
        primary_artist = artist.get("name")
        # "contributors" (artistes en featuring) n'existe que sur /track/{id} et
        # /artist/{id}/top — absent sur /search/track et la tracklist de /album/{id}.
        # None = information non disponible à cet endpoint, à ne pas confondre avec
        # [] qui signifierait "vérifié, aucun featuring" (sinon on renverrait une
        # fausse info : "pas de featuring" alors qu'on n'a simplement pas vérifié).
        contributors = raw.get("contributors")
        featured_artists = (
            None
            if contributors is None
            else [c["name"] for c in contributors if c.get("name") != primary_artist]
        )
        return {
            "id": raw["id"],
            "title": raw["title"],
            "artist": primary_artist,
            "featured_artists": featured_artists,
            "album": album.get("title"),
            "album_id": album.get("id"),
            "duration": raw.get("duration"),
            "preview": raw.get("preview"),
            "link": raw.get("link"),
        }

    @staticmethod
    def _shape_album(raw: dict) -> dict:
        artist = raw.get("artist") or {}
        return {
            "id": raw["id"],
            "title": raw["title"],
            "artist": artist.get("name"),
            "release_date": raw.get("release_date"),
            "nb_tracks": raw.get("nb_tracks"),
            "cover": raw.get("cover_medium"),
            "link": raw.get("link"),
        }

    @staticmethod
    def _shape_artist(raw: dict) -> dict:
        return {
            "id": raw["id"],
            "name": raw["name"],
            "nb_fan": raw.get("nb_fan"),
            "nb_album": raw.get("nb_album"),
            "picture": raw.get("picture_medium"),
            "link": raw.get("link"),
        }
