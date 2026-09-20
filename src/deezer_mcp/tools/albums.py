from mcp.server.mcpserver import MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def get_album(album_id: int) -> dict:
        """Récupère les infos d'un album Deezer (titre, artiste, date de sortie, pochette)
        ainsi que sa tracklist complète.

        Le champ `cover` est une URL de référence Deezer (à ouvrir dans un navigateur),
        pas une image directement affichable dans la réponse.

        Chaque titre inclut le champ `preview` (URL vers l'extrait audio, 30 secondes) à
        présenter à l'utilisateur en lien cliquable.
        """
        return await client.get_album(album_id)
