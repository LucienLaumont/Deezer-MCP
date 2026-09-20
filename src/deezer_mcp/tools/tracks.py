from mcp.server.mcpserver import Audio, MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def get_track(track_id: int) -> dict:
        """Récupère les détails d'un titre Deezer à partir de son ID.

        Inclut l'URL `preview` (extrait audio MP3 de 30 secondes) à utiliser pour l'écoute.
        """
        return await client.get_track(track_id)

    @mcp.tool()
    async def get_track_audio(track_id: int) -> Audio:
        """Télécharge l'extrait audio (30 secondes, MP3) d'un titre Deezer et le renvoie
        directement en tant que contenu audio jouable.

        Différent de `get_track` : celui-ci ne renvoie qu'une URL (qui peut être bloquée
        par certains clients pour des raisons de sécurité réseau), alors que `get_track_audio`
        télécharge les données audio elles-mêmes côté serveur et les renvoie prêtes à jouer.
        Plus coûteux (téléchargement ~500 Ko) : à utiliser seulement quand l'utilisateur
        veut vraiment écouter un titre précis, pas pour explorer plusieurs résultats.
        """
        audio_bytes = await client.fetch_preview_audio(track_id)
        return Audio(data=audio_bytes, format="mpeg")  # -> mime_type "audio/mpeg" (standard, validé)
