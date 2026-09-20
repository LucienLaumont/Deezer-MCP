from mcp.server.mcpserver import MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def search_tracks(query: str, limit: int = 10) -> list[dict]:
        """Recherche des titres sur Deezer par texte libre (nom de titre, artiste, album...).

        Renvoie une liste de titres avec leur artiste, leur album, et le champ `preview`
        (URL vers l'extrait audio, 30 secondes) à présenter à l'utilisateur en lien cliquable.

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
        """Recherche des albums sur Deezer par texte libre (titre d'album ou nom d'artiste).

        Le champ `cover` est une URL de référence, PAS chargeable directement dans un
        Artifact. Pour afficher réellement la pochette, utiliser `get_album_cover` sur l'ID.
        """
        return await client.search_albums(query, limit)

    @mcp.tool()
    async def search_artists(query: str, limit: int = 10) -> list[dict]:
        """Recherche des artistes sur Deezer par nom.

        Renvoie plusieurs candidats avec leur nombre de fans (`nb_fan`), ce qui permet
        de distinguer un artiste populaire d'un simple homonyme peu connu — utile
        quand la requête contient une faute d'orthographe (le matching Deezer est flou
        et pondéré par popularité, mais pas garanti de renvoyer le bon artiste en premier).

        Le champ `picture` est une URL de référence, PAS chargeable directement dans un
        Artifact. Pour afficher réellement la photo, utiliser `get_artist_picture` sur l'ID.
        """
        return await client.search_artists(query, limit)
