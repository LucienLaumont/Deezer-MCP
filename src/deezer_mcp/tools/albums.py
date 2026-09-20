from mcp.server.mcpserver import Image, MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def get_album(album_id: int) -> dict:
        """Récupère les infos d'un album Deezer (titre, artiste, date de sortie, pochette)
        ainsi que sa tracklist complète.

        Le champ `cover` est une URL de référence, PAS chargeable directement dans un
        Artifact (bloquée par la liste blanche du sandbox). Pour afficher réellement la
        pochette dans une réponse visuelle, utiliser `get_album_cover` sur cet ID.

        Chaque titre inclut le champ `preview` (URL vers l'extrait audio, 30 secondes) à
        présenter à l'utilisateur en lien cliquable.
        """
        return await client.get_album(album_id)

    @mcp.tool()
    async def get_album_cover(album_id: int) -> Image:
        """Renvoie la pochette d'un album Deezer en image directement affichable.

        À utiliser quand l'utilisateur veut voir la pochette (ex: dans une carte visuelle
        en Artifact) — le champ `cover` de `get_album`/`search_albums` n'est qu'une URL,
        non chargeable directement dans un Artifact.
        """
        image_bytes = await client.fetch_album_cover(album_id)
        return Image(data=image_bytes, format="jpeg")
