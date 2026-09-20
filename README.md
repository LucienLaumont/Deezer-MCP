# Deezer MCP

Serveur MCP (Model Context Protocol) exposant le catalogue public Deezer — recherche de titres/albums/artistes et écoute des previews audio 30s — à des clients compatibles MCP comme Claude.

Statut : 6 tools implémentés et testés (Inspector + Claude Code en local), transports `stdio` et `streamable-http` fonctionnels. Déploiement distant (Render) à venir.

Testé en conditions réelles avec `search_artists` → `get_artist_top_tracks` via Claude Code (voir historique du projet) : le modèle choisit correctement le bon tool, désambiguïse les homonymes via `nb_fan`, et récupère des previews jouables.

## Tools disponibles

| Tool | Description |
|---|---|
| `search_tracks(query, limit=10)` | Recherche de titres par texte libre |
| `search_albums(query, limit=10)` | Recherche d'albums par texte libre |
| `search_artists(query, limit=10)` | Recherche d'artistes par nom (renvoie `nb_fan` pour désambiguïser les homonymes) |
| `get_track(track_id)` | Détails d'un titre + preview audio |
| `get_album(album_id)` | Détails d'un album + tracklist complète (previews incluses) |
| `get_artist_top_tracks(artist_id, limit=10)` | Titres les plus populaires d'un artiste |

Chaque tool renvoie des champs "propres" (id, title, artist, album, duration, `preview`, link) plutôt que la réponse brute Deezer — la logique de nettoyage vit dans `DeezerClient`.

⚠️ Note : `search_albums` ne renvoie pas `release_date` (champ absent de `/search/album`, contrairement à `/album/{id}` utilisé par `get_album`) — vérifié en direct sur l'API, pas un bug.

## Structure

```
src/deezer_mcp/
├── server.py           # instance MCPServer, câblage des tools, point d'entrée
├── deezer_client.py     # client HTTP vers api.deezer.com + nettoyage des réponses
└── tools/               # un fichier par groupe de tools (search, tracks, albums, artists)
docs/
└── deezer-api.md        # doc de référence de l'API Deezer, vérifiée en direct
```

## Setup local

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e .
```

## Lancer le serveur

Local (dev, transport `stdio`, utilisé par `.mcp.json` / `mcp dev`) :
```bash
python -m deezer_mcp.server
```

Distant (transport `streamable-http`, utilisé sur Render) :
```bash
MCP_TRANSPORT=streamable-http PORT=8000 python -m deezer_mcp.server
```
Écoute sur `0.0.0.0:$PORT`, endpoint MCP exposé sur `/mcp`. `PORT` est fourni automatiquement par Render.

Voir [docs/deezer-api.md](docs/deezer-api.md) pour la référence de l'API Deezer utilisée.
