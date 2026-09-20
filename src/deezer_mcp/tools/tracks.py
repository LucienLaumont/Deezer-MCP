from mcp.server.mcpserver import MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def get_track(track_id: int) -> dict:
        """Récupère les détails d'un titre Deezer à partir de son ID.

        Inclut l'URL `preview` (extrait audio MP3 de 30 secondes) à utiliser pour l'écoute.
        """
        return await client.get_track(track_id)
