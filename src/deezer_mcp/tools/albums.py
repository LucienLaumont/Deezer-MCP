from mcp.server.mcpserver import MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def get_album(album_id: int) -> dict:
        """Récupère les infos d'un album Deezer (titre, artiste, date de sortie, pochette)
        ainsi que sa tracklist complète, chaque titre incluant son URL `preview` audio.
        """
        return await client.get_album(album_id)
