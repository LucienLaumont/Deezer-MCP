from mcp.server.mcpserver import Audio, MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def get_track(track_id: int) -> dict:
        """Récupère les détails d'un titre Deezer à partir de son ID.

        Inclut le champ `preview`, une URL de référence vers l'extrait audio Deezer (30s).
        Cette URL n'est PAS jouable directement dans la plupart des clients (bloquée par
        les vérifications de sécurité réseau des sandboxes) — elle sert seulement de
        référence/lien à afficher. Si l'utilisateur veut réellement écouter le titre,
        utiliser `get_track_audio` sur ce même ID, qui renvoie l'audio jouable directement.
        """
        return await client.get_track(track_id)

    @mcp.tool()
    async def get_track_audio(track_id: int) -> Audio:
        """Renvoie l'extrait audio jouable (30 secondes, MP3) d'un titre Deezer.

        À utiliser chaque fois que l'utilisateur veut réellement ÉCOUTER un titre précis
        (pas juste consulter ses infos). Contrairement au champ `preview` renvoyé par
        `get_track`/`search_tracks`/etc. (une simple URL, non jouable directement dans la
        plupart des clients), ce tool télécharge les données audio côté serveur et les
        renvoie prêtes à jouer. Plus coûteux (~500 Ko par appel) : à réserver au titre que
        l'utilisateur veut vraiment écouter, pas à toute une liste de résultats.
        """
        audio_bytes = await client.fetch_preview_audio(track_id)
        return Audio(data=audio_bytes, format="mpeg")  # -> mime_type "audio/mpeg" (standard, validé)
