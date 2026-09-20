from mcp.server.mcpserver import MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def get_track(track_id: int) -> dict:
        """Récupère les détails d'un titre Deezer à partir de son ID.

        Inclut le champ `preview`, une URL vers l'extrait audio Deezer (30s) à présenter
        à l'utilisateur en lien cliquable, et `album_id` (utilisable directement avec
        `get_album_cover` pour la pochette).
        """
        return await client.get_track(track_id)
