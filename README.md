# Deezer MCP

Serveur MCP (Model Context Protocol) exposant le catalogue public Deezer — recherche de titres/albums/artistes et écoute des previews audio 30s — à des clients compatibles MCP comme Claude.

Statut : squelette du projet, tools pas encore implémentés.

## Structure

```
src/deezer_mcp/
├── server.py         # instance FastMCP, point d'entrée
├── deezer_client.py   # client HTTP vers api.deezer.com
└── tools/             # un fichier par groupe de tools (à venir)
docs/
└── deezer-api.md      # doc de référence de l'API Deezer, vérifiée en direct
```

## Setup local

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e .
```

## Lancer le serveur (dev, transport stdio)

```bash
python -m deezer_mcp.server
```

Voir [docs/deezer-api.md](docs/deezer-api.md) pour la référence de l'API Deezer utilisée.
