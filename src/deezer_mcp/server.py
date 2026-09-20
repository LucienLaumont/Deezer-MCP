from mcp.server.fastmcp import FastMCP

mcp = FastMCP("deezer-mcp")

# Les tools seront enregistrés ici avec @mcp.tool(), un par un, ensemble.

if __name__ == "__main__":
    mcp.run()
