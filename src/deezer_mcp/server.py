import os

from mcp.server.mcpserver import MCPServer

from deezer_mcp.deezer_client import DeezerClient
from deezer_mcp.tools import albums, artists, search, tracks

mcp = MCPServer(
    "deezer-mcp",
    instructions=(
        "Les URLs renvoyées par ce serveur (`preview`, `link`) contiennent des paramètres "
        "techniques longs (jeton d'authentification temporaire pour le streaming). Quand tu "
        "présentes une de ces URLs à l'utilisateur, formate-la toujours en lien Markdown avec "
        "un texte descriptif court, jamais l'URL brute — par exemple "
        "`[🎧 Écouter l'extrait (30s)](url)` ou `[🎵 Écouter en entier sur Deezer](url)`.\n\n"
        "Les champs `cover` (album) et `picture` (artiste) sont aussi de simples URLs de "
        "référence, non chargeables directement dans un Artifact (liste blanche du sandbox). "
        "Pour afficher réellement une pochette ou une photo d'artiste dans une réponse "
        "visuelle, utiliser `get_album_cover` ou `get_artist_picture` sur l'ID correspondant, "
        "qui renvoient l'image directement."
    ),
)
_client = DeezerClient()

search.register(mcp, _client)
tracks.register(mcp, _client)
albums.register(mcp, _client)
artists.register(mcp, _client)

if __name__ == "__main__":
    # Local (mcp dev, Claude Code) : stdio par défaut, rien à configurer.
    # Render (déploiement distant) : MCP_TRANSPORT=streamable-http, PORT fourni par Render.
    if os.environ.get("MCP_TRANSPORT") == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    else:
        mcp.run(transport="stdio")
