# Roadmap

Pistes pour renforcer le projet côté portfolio (automatisation, qualité, maîtrise du protocole MCP). Pas encore implémenté — liste de travail.

## 1. Tests + CI (priorité)

- [x] Suite de tests `pytest` pour `DeezerClient` (`tests/test_deezer_client.py`, mock `httpx` via `respx`) : `_shape_track`/`_shape_album`/`_shape_artist`/`_shape_genre`, la gestion d'erreur (`DeezerAPIError` sur payload `error`, HTTP error, erreur réseau) et les nouvelles méthodes composites/chart/genre, sans dépendre du vrai réseau.
- [x] Tests des tools eux-mêmes (`tests/test_tools.py`, via `mcp.call_tool()` en mémoire) : câblage de chaque tool au client, et logique propre aux tools composites (résolution par nom la plus populaire, validation des paramètres de `get_artist_profile`).
- [ ] Pipeline GitHub Actions (`.github/workflows/ci.yml`) : install, lint (`ruff`?), tests, à chaque push/PR sur `main`.
- [ ] Badge de statut CI dans le README une fois en place.

## 2. Autres primitives MCP (resources & prompts)

Le projet n'utilise que des *tools*. Explorer les deux autres primitives du protocole pour montrer une maîtrise plus complète :
- [ ] **Resource** : exposer `docs/deezer-api.md` (ou un résumé des capacités du serveur) comme ressource MCP consultable par le client, plutôt que seulement via les docstrings de tools.
- [ ] **Prompt** : définir un prompt réutilisable côté serveur (ex: un template "fiche artiste" qui enchaîne `search_artists` → `get_artist_top_tracks`), pour montrer comment un serveur MCP peut aussi guider l'usage, pas juste exposer des fonctions.
- [ ] Vérifier comment chaque primitive apparaît côté client (claude.ai, Claude Code) avant d'investir trop de temps — comme pour les tools, le support client peut être partiel.

## 3. Robustesse / production readiness

- [ ] Rate limiting côté serveur (par IP ou par session) — le serveur est public sur Render depuis le déploiement, jamais protégé contre l'abus. Point explicitement identifié puis reporté "à la phase de déploiement".
- [ ] Cache en mémoire (TTL court) pour les recherches/lookups répétés — évite de retaper l'API Deezer (limite ~50 req/5s) si plusieurs utilisateurs interrogent la même chose.
- [ ] Logging structuré des appels de tools (utile pour observer l'usage réel une fois le serveur partagé plus largement).

## 4. Nettoyage mineur (déjà identifié, jamais fait)

- [ ] Retirer `uv.lock` du repo (le projet utilise `pip`, pas `uv` — fichier resté par erreur).
- [ ] Rendre le chemin dans `.mcp.json` portable (actuellement un chemin Windows absolu propre à cette machine).

## 5. Retenu : orchestration agentique

Scope validé — deux nouveaux tools, tous deux basés sur des endpoints Deezer déjà documentés mais jamais wrappés (`docs/deezer-api.md` §3.4, §3.6) :

- [x] **Fiche artiste enrichie** (tool composite) : `get_artist_profile` enchaîne côté serveur `get_artist` → `get_artist_top_tracks` → `/artist/{id}/related` (artistes similaires), renvoyés en une seule réponse. Accepte `artist_id` ou `artist_name` (résolution auto par nb de fans, le tri par pertinence Deezer n'étant pas fiable pour repérer l'artiste le plus connu).
- [x] **Générateur de playlist par ambiance** : `list_genres` + `get_chart_tracks` (`/genre`, `/chart`, `/chart/{genre_id}`) exposés pour que le modèle compose lui-même une sélection cohérente à partir d'une description en langage naturel. L'intelligence reste côté modèle ; le tool fournit la matière première (charts par genre) plutôt que de faire du NLP côté serveur.

Pas retenu pour l'instant (mis en pause, pas abandonné) : profondeur protocole (resources/prompts/elicitation/sampling) et brique ML (recherche par embeddings) — cf. section 2 plus haut, à reprendre après ces deux tools.

## 6. Démo publique (GitHub Pages)

- [ ] Page statique de présentation du projet une fois les deux tools ci-dessus en place.
- [ ] **Vidéo réelle** capturée d'une session Claude utilisant le MCP (recherche, previews, fiche artiste, playlist par ambiance) — pas de faux live chat, GitHub Pages est statique.
- [ ] Explicitement exclu : chat live embarqué dans la page (nécessiterait un backend proxy + gestion de coût/abus — hors scope pour une page de démo statique).

**Format de la vidéo** (référence : démo Blender MCP, en plus lent) :
- Chat en plein écran (Claude Desktop ou claude.ai), pas de split-screen.
- Vraie interaction tapée en direct (pas un agent autonome qui s'exécute seul) — l'utilisateur pose chaque question à la main.
- Aucune narration parlée : silence pendant la capture, avec de vraies pauses volontaires après chaque réponse pour laisser de la place aux captions ajoutées au montage.
- Chaque tool call déplié manuellement (repliés par défaut dans l'UI Claude) et laissé assez longtemps à l'écran pour être lisible avant de couper — c'est ce qui donne le rythme "lent" et la lisibilité des appels d'outils.
- Montage (CapCut ou DaVinci Resolve, gratuits sur Windows) : captions texte synchronisées sur les pauses, zoom ciblé sur les blocs de tool call / réponses clés.
