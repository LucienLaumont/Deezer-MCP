from mcp.server.mcpserver import MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def get_album(album_id: int) -> dict:
        """Récupère les infos d'un album Deezer (titre, artiste, date de sortie, pochette)
        ainsi que sa tracklist complète. Chaque titre inclut le champ `preview` (URL de
        référence, 30 secondes), qui n'est PAS jouable directement dans la plupart des
        clients. Pour écouter réellement un des titres de l'album, utiliser `get_track_audio`
        sur son ID.
        """
        return await client.get_album(album_id)
