# Deezer MCP

Serveur MCP (Model Context Protocol) exposant le catalogue public Deezer — recherche de titres/albums/artistes et écoute des previews audio 30s — à des clients compatibles MCP comme Claude.

Statut : 8 tools implémentés et testés en conditions réelles, déployé sur Render (transport `streamable-http`), testé avec succès dans claude.ai et Claude Code.

Testé en conditions réelles avec `search_artists` → `get_artist_top_tracks` via Claude Code : le modèle choisit correctement le bon tool, désambiguïse les homonymes via `nb_fan`, et récupère des previews. Testé aussi sur claude.ai : le lien de preview renvoyé s'ouvre et joue correctement dans le navigateur.

## Tools disponibles

| Tool | Description |
|---|---|
| `search_tracks(query, limit=10)` | Recherche de titres par texte libre |
| `search_albums(query, limit=10)` | Recherche d'albums par texte libre |
| `search_artists(query, limit=10)` | Recherche d'artistes par nom (renvoie `nb_fan` pour désambiguïser les homonymes) |
| `get_track(track_id)` | Détails d'un titre + preview audio |
| `get_album(album_id)` | Détails d'un album + tracklist complète (previews incluses) |
| `get_artist_top_tracks(artist_id, limit=10)` | Titres les plus populaires d'un artiste |
| `get_album_cover(album_id)` | Pochette d'un album en image directement affichable (pas juste une URL) |
| `get_artist_picture(artist_id)` | Photo d'un artiste en image directement affichable (pas juste une URL) |

Chaque tool renvoie des champs "propres" (id, title, artist, album, duration, `preview`, link) plutôt que la réponse brute Deezer — la logique de nettoyage vit dans `DeezerClient`.

### Écoute des previews : pourquoi un simple lien, et pas de l'audio embarqué

Piste explorée puis abandonnée : renvoyer l'audio directement dans la réponse d'un tool (type `AudioContent` du SDK MCP, bytes MP3 encodés) plutôt qu'une simple URL. Techniquement ça fonctionne (vérifié en local et sur le serveur distant), mais le rendu côté client est inconsistant selon l'interface Claude : Claude Code télécharge le fichier sur disque plutôt que de l'intégrer au chat, et claude.ai continue de préférer donner un lien cliquable même quand cet outil est disponible. Le gain de fiabilité n'existait pas, seulement de la complexité en plus (téléchargement ~500 Ko côté serveur par appel) — retiré.

Solution retenue, plus simple : le champ `preview` reste une URL, et le serveur MCP définit un champ `instructions` (transmis une fois au client à la connexion) qui demande explicitement de présenter les URLs renvoyées en lien Markdown avec texte descriptif plutôt qu'en URL brute (qui contient un jeton d'authentification long et illisible). Voir `server.py`.

### Pochettes et photos d'artiste : pourquoi deux tools séparés, contrairement à l'audio

Même contrainte de sandbox que l'audio (liste blanche restreinte à quelques CDN de librairies JS/CSS/fonts — ni Deezer, ni aucun domaine externe arbitraire, vérifié empiriquement même pour un domaine sans rapport avec Deezer). Contrairement à l'audio où un simple lien cliquable est une alternative pleinement valable (cliquer = écouter), il n'y a pas d'équivalent pour une image : un lien vers une pochette ne l'affiche pas dans la réponse, il faut cliquer et quitter la conversation. D'où le choix, cette fois, de garder `get_album_cover`/`get_artist_picture` comme tools dédiés — l'image est encodée en base64 (`ImageContent`), ce qui contourne le sandbox puisqu'aucune requête réseau n'est faite au moment de l'affichage.

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
