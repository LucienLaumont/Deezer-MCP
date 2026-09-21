# Deezer MCP

Serveur MCP (Model Context Protocol) exposant le catalogue public Deezer — recherche de titres/albums/artistes et écoute des previews audio 30s — à des clients compatibles MCP comme Claude.

Statut : 9 tools implémentés et testés en conditions réelles, déployé sur Render (transport `streamable-http`), testé avec succès dans claude.ai et Claude Code.

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
| `get_artist_profile(artist_id=None, artist_name=None, ...)` | Tool composite : fiche artiste + top titres + artistes similaires en un seul appel. Accepte un ID ou un nom (résolu vers le candidat le plus populaire) |
| `list_genres()` | Liste des genres Deezer (id + nom), pour cibler `get_chart_tracks` |
| `get_chart_tracks(genre_id=None, limit=10)` | Titres populaires du moment, globalement ou par genre — matière première pour une playlist par ambiance composée par le modèle |

Chaque tool renvoie des champs "propres" (id, title, artist, album, duration, `preview`, link) plutôt que la réponse brute Deezer — la logique de nettoyage vit dans `DeezerClient`.

### Écoute des previews : pourquoi un simple lien, et pas de l'audio embarqué

Piste explorée puis abandonnée : renvoyer l'audio directement dans la réponse d'un tool (type `AudioContent` du SDK MCP, bytes MP3 encodés) plutôt qu'une simple URL. Techniquement ça fonctionne (vérifié en local et sur le serveur distant), mais le rendu côté client est inconsistant selon l'interface Claude : Claude Code télécharge le fichier sur disque plutôt que de l'intégrer au chat, et claude.ai continue de préférer donner un lien cliquable même quand cet outil est disponible. Le gain de fiabilité n'existait pas, seulement de la complexité en plus (téléchargement ~500 Ko côté serveur par appel) — retiré.

Solution retenue, plus simple : le champ `preview` reste une URL, et le serveur MCP définit un champ `instructions` (transmis une fois au client à la connexion) qui demande explicitement de présenter les URLs renvoyées en lien Markdown avec texte descriptif plutôt qu'en URL brute (qui contient un jeton d'authentification long et illisible). Voir `server.py`.

### Pochettes et photos d'artiste : tools essayés puis retirés

Piste explorée : deux tools dédiés, `get_album_cover(album_id)` et `get_artist_picture(artist_id)`, renvoyant l'image encodée en base64 (`ImageContent`, contourne le sandbox puisqu'aucune requête réseau n'a lieu au moment de l'affichage) **et** la même image sous forme de chaîne `data:image/jpeg;base64,...` en texte brut (`TextContent`), pour que le modèle appelant puisse la recopier littéralement dans un `<img src="...">` d'un Artifact/widget.

Ça a d'abord semblé résoudre le problème : un premier test sur Claude Desktop affichait bien une image dans le widget. Mais en vérifiant, deux appels réels au même tool (même artiste) ont donné deux résultats très différents une fois copiés dans un Artifact :
- Un cas où le texte recopié était **strictement identique** à la référence renvoyée par le serveur (même longueur, même SHA256).
- Un cas où le texte recopié faisait **1834 caractères de plus**, avec un SHA256 totalement différent — malgré les 40 premiers caractères identiques (preuve que la bonne image avait bien été reçue au départ, mais que la copie a divergé en cours de route, vraisemblablement par duplication accidentelle d'un segment).

Vérifié directement en interrogeant le serveur déployé et en comparant des empreintes SHA256 (longueur + hash), pas par relecture visuelle : le serveur renvoie toujours la bonne donnée. Le problème se situe entièrement une étape plus loin, dans la capacité du modèle appelant à reproduire ~13-15 Ko de texte opaque (non-linguistique, donc sans les régularités qui aident normalement un modèle de langage à rester cohérent sur une longue séquence) sans erreur au moment de générer le HTML de l'Artifact. Rien ne garantit ce résultat : ça peut réussir une fois et échouer la suivante, sans erreur visible côté serveur ni côté client.

Comme il n'y a pas de fix possible côté serveur MCP à ce problème — il vit entièrement dans l'étape de génération du modèle, hors de notre contrôle — les deux tools ont été retirés plutôt que gardés comme fonctionnalité non fiable. Note : la perception native de l'image (le modèle "voit" et décrit la photo sans avoir besoin de la recopier en texte) fonctionnait bien de façon isolée, mais ce n'était pas l'usage recherché ici (affichage visuel dans une réponse riche).

⚠️ Note : `search_albums` ne renvoie pas `release_date` (champ absent de `/search/album`, contrairement à `/album/{id}` utilisé par `get_album`) — vérifié en direct sur l'API, pas un bug.

## Structure

```
src/deezer_mcp/
├── server.py           # instance MCPServer, câblage des tools, point d'entrée
├── deezer_client.py     # client HTTP vers api.deezer.com + nettoyage des réponses
└── tools/               # un fichier par groupe de tools (search, tracks, albums, artists, discovery)
tests/
├── factories.py         # constructeurs de payloads Deezer bruts pour les tests
├── test_deezer_client.py # DeezerClient : shaping, gestion d'erreur, mocké via respx
└── test_tools.py         # tools MCP : câblage + logique propre aux tools composites
docs/
└── deezer-api.md        # doc de référence de l'API Deezer, vérifiée en direct
```

## Setup local

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e ".[dev]"   # inclut pytest/respx pour lancer les tests
```

## Tests

```bash
pytest
```

Aucune requête réseau réelle : `DeezerClient` est mocké via `respx` (au niveau transport `httpx`), y compris pour les tools appelés via `mcp.call_tool()` en mémoire.

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
