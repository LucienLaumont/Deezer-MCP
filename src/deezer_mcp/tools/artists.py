from mcp.server.mcpserver import MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def get_artist_top_tracks(artist_id: int, limit: int = 10) -> list[dict]:
        """Récupère les titres les plus populaires d'un artiste Deezer à partir de son ID.

        Chaque titre inclut le champ `preview` (URL vers l'extrait audio, 30 secondes) à
        présenter à l'utilisateur en lien cliquable, et `album_id` (retrouvable directement
        sans repasser par `search_albums`).
        """
        return await client.get_artist_top_tracks(artist_id, limit)

    @mcp.tool()
    async def get_artist_profile(
        artist_id: int | None = None,
        artist_name: str | None = None,
        top_tracks_limit: int = 10,
        related_limit: int = 5,
    ) -> dict:
        """Fiche artiste enrichie : combine en un seul appel les infos de l'artiste,
        ses titres les plus populaires et des artistes similaires (`related_artists`,
        pour rebondir vers une découverte).

        Fournir soit `artist_id` (si déjà connu), soit `artist_name` (le meilleur
        candidat est résolu automatiquement en interne via une recherche, sans avoir
        besoin d'appeler `search_artists` séparément avant). Fournir exactement un des
        deux, pas les deux, pas aucun.

        Note sur la résolution par nom : le tri par pertinence de Deezer n'est pas
        fiable pour repérer l'artiste le plus connu (un homonyme obscur peut sortir
        avant l'artiste populaire recherché). Le candidat retenu est donc celui avec
        le plus de fans (`nb_fan`) parmi les premiers résultats, pas simplement le
        premier renvoyé par l'API.

        Chaque titre de `top_tracks` inclut `preview` (extrait audio 30s) à présenter
        en lien cliquable. Les champs `picture` (artiste) sont des URLs de référence
        Deezer, à présenter en lien, pas affichables comme image dans la réponse.
        """
        if (artist_id is None) == (artist_name is None):
            raise ValueError("Fournir soit artist_id, soit artist_name (un seul des deux).")
        if artist_name is not None:
            candidates = await client.search_artists(artist_name, limit=10)
            if not candidates:
                raise ValueError(f"Aucun artiste Deezer trouvé pour {artist_name!r}.")
            best = max(candidates, key=lambda a: a.get("nb_fan") or 0)
            artist_id = best["id"]
        return await client.get_artist_profile(artist_id, top_tracks_limit, related_limit)
