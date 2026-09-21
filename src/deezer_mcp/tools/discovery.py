from mcp.server.mcpserver import MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def list_genres() -> list[dict]:
        """Liste les genres musicaux disponibles sur Deezer (id + nom), ex: Pop, Rap,
        Electro, Rock...

        À utiliser avant `get_chart_tracks` pour connaître les `genre_id` valides —
        utile par exemple pour composer une playlist par ambiance à partir d'une
        description libre ("musique énergique pour courir" → repérer un genre proche
        comme Electro/Dance dans cette liste, puis appeler `get_chart_tracks` dessus).
        Le genre d'id 0 ("Tous") correspond au chart global, tous genres confondus.
        """
        return await client.get_genres()

    @mcp.tool()
    async def get_chart_tracks(
        genre_id: int | None = None, limit: int = 10
    ) -> list[dict]:
        """Titres les plus populaires du moment sur Deezer (chart), globalement ou
        pour un genre précis (`genre_id`, voir `list_genres`).

        Ne fait aucune analyse d'ambiance ni de NLP côté serveur : fournit juste la
        matière première (des titres populaires par genre) pour que le modèle compose
        lui-même une sélection cohérente avec la demande de l'utilisateur — par exemple
        en combinant les charts de plusieurs genres pertinents pour une ambiance donnée.

        Chaque titre inclut `preview` (extrait audio 30s) à présenter en lien cliquable.
        """
        return await client.get_chart_tracks(genre_id, limit)
