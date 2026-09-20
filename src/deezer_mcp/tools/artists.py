import base64

from mcp.server.mcpserver import Image, MCPServer

from deezer_mcp.deezer_client import DeezerClient


def register(mcp: MCPServer, client: DeezerClient) -> None:
    @mcp.tool()
    async def get_artist_top_tracks(artist_id: int, limit: int = 10) -> list[dict]:
        """Récupère les titres les plus populaires d'un artiste Deezer à partir de son ID.

        Chaque titre inclut le champ `preview` (URL vers l'extrait audio, 30 secondes) à
        présenter à l'utilisateur en lien cliquable, et `album_id` : utiliser directement
        cet ID avec `get_album_cover` pour la pochette, pas besoin de repasser par
        `search_albums` pour le retrouver.
        """
        return await client.get_artist_top_tracks(artist_id, limit)

    @mcp.tool()
    async def get_artist_picture(artist_id: int) -> list[Image | str]:
        """Renvoie la photo d'un artiste Deezer, en image ET en URI `data:` texte brut.

        À utiliser quand l'utilisateur veut voir une photo de l'artiste (ex: dans une carte
        visuelle en Artifact) — le champ `picture` de `search_artists` n'est qu'une URL,
        non chargeable directement dans un Artifact.

        Le résultat contient deux éléments : l'image elle-même (pour la percevoir/décrire),
        ET une chaîne de texte `data:image/jpeg;base64,...` prête à copier directement dans
        un attribut `src` d'un `<img>` en HTML — certains clients reçoivent l'image comme
        contenu visuel sans donner accès au texte brut correspondant, cette deuxième valeur
        évite d'avoir à retélécharger ou reconstruire quoi que ce soit pour l'intégrer.
        """
        image_bytes = await client.fetch_artist_picture(artist_id)
        data_uri = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('ascii')}"
        return [Image(data=image_bytes, format="jpeg"), data_uri]
