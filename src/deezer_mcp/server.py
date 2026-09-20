import os

from mcp.server.mcpserver import MCPServer

from deezer_mcp.deezer_client import DeezerClient
from deezer_mcp.tools import albums, artists, search, tracks

mcp = MCPServer("deezer-mcp")
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
