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
    mcp.run()
