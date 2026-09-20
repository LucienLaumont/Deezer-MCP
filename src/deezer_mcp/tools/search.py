from mcp.server.mcpserver import MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def search_tracks(query: str, limit: int = 10) -> list[dict]:
        """Recherche des titres sur Deezer par texte libre (nom de titre, artiste, album...).

        Renvoie une liste de titres avec leur artiste, leur album, et le champ `preview`
        (URL de référence vers l'extrait audio, 30 secondes) — cette URL n'est PAS jouable
        directement dans la plupart des clients (bloquée par les vérifications de sécurité
        réseau des sandboxes), elle sert seulement de lien de référence. Si l'utilisateur
        veut réellement écouter un des titres trouvés, utiliser `get_track_audio` sur son ID.

        Attention : une recherche par nom d'artiste peut renvoyer des titres où cet
        artiste n'est que featuring (ex: chercher "Daft Punk" peut renvoyer des titres
        de The Weeknd sur lesquels Daft Punk apparaît en featuring). Cet endpoint ne
        fournit pas les crédits de featuring : `featured_artists` vaudra `null`
        (information non disponible, à ne pas lire comme "aucun featuring"). Utiliser
        `get_track` sur l'ID d'un résultat pour obtenir les crédits complets.
        """
        return await client.search_tracks(query, limit)

    @mcp.tool()
    async def search_albums(query: str, limit: int = 10) -> list[dict]:
        """Recherche des albums sur Deezer par texte libre (titre d'album ou nom d'artiste)."""
        return await client.search_albums(query, limit)

    @mcp.tool()
    async def search_artists(query: str, limit: int = 10) -> list[dict]:
        """Recherche des artistes sur Deezer par nom.

        Renvoie plusieurs candidats avec leur nombre de fans (`nb_fan`), ce qui permet
        de distinguer un artiste populaire d'un simple homonyme peu connu — utile
        quand la requête contient une faute d'orthographe (le matching Deezer est flou
        et pondéré par popularité, mais pas garanti de renvoyer le bon artiste en premier).
        """
        return await client.search_artists(query, limit)
