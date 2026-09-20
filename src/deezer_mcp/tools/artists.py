from mcp.server.mcpserver import Image, MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def get_artist_top_tracks(artist_id: int, limit: int = 10) -> list[dict]:
        """Récupère les titres les plus populaires d'un artiste Deezer à partir de son ID.

        Chaque titre inclut le champ `preview` (URL vers l'extrait audio, 30 secondes) à
        présenter à l'utilisateur en lien cliquable.
        """
        return await client.get_artist_top_tracks(artist_id, limit)

    @mcp.tool()
    async def get_artist_picture(artist_id: int) -> Image:
        """Renvoie la photo d'un artiste Deezer en image directement affichable.

        À utiliser quand l'utilisateur veut voir une photo de l'artiste (ex: dans une carte
        visuelle en Artifact) — le champ `picture` de `search_artists` n'est qu'une URL,
        non chargeable directement dans un Artifact.
        """
        image_bytes = await client.fetch_artist_picture(artist_id)
        return Image(data=image_bytes, format="jpeg")
