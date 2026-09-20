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
