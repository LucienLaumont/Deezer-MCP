from mcp.server.mcpserver import MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def get_artist_top_tracks(artist_id: int, limit: int = 10) -> list[dict]:
        """Récupère les titres les plus populaires d'un artiste Deezer à partir de son ID.

        Chaque titre inclut le champ `preview` (URL de référence, 30 secondes), qui n'est
        PAS jouable directement dans la plupart des clients. Pour écouter réellement un
        des titres trouvés, utiliser `get_track_audio` sur son ID.
        """
        return await client.get_artist_top_tracks(artist_id, limit)
