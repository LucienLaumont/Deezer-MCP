# Roadmap

Pistes pour renforcer le projet côté portfolio (automatisation, qualité, maîtrise du protocole MCP). Pas encore implémenté — liste de travail.

## 1. Tests + CI (priorité)

- [ ] Suite de tests `pytest` pour `DeezerClient` : mocker `httpx` (via `httpx.MockTransport` ou `respx`) pour tester `_shape_track`/`_shape_album`/`_shape_artist` et la gestion d'erreur (`DeezerAPIError`) sans dépendre du vrai réseau.
- [ ] Tests des tools eux-mêmes (appel direct des fonctions enregistrées, ou via un client MCP en mémoire).
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

- [ ] **Fiche artiste enrichie** (tool composite) : enchaîne côté serveur `search_artists` (ou un ID direct) → `get_artist_top_tracks` → `/artist/{id}/related` (artistes similaires), renvoyés en une seule réponse. Illustre une orchestration pensée pour réduire les aller-retours du modèle, pas juste un mapping 1 endpoint = 1 tool.
- [ ] **Générateur de playlist par ambiance** : à partir d'une description en langage naturel ("musique énergique pour courir"), exposer les bons blocs (`/chart`, `/chart/{genre_id}`, `/genre`) pour que le modèle compose lui-même une sélection cohérente. L'intelligence reste côté modèle ; le tool fournit la matière première pertinente (charts par genre) plutôt que de faire du NLP côté serveur.

Pas retenu pour l'instant (mis en pause, pas abandonné) : profondeur protocole (resources/prompts/elicitation/sampling) et brique ML (recherche par embeddings) — cf. section 2 plus haut, à reprendre après ces deux tools.

## 6. Démo publique (GitHub Pages)

- [ ] Page statique de présentation du projet une fois les deux tools ci-dessus en place.
- [ ] **Vidéo réelle** capturée d'une session Claude utilisant le MCP (recherche, previews, fiche artiste, playlist par ambiance) — pas de faux live chat, GitHub Pages est statique.
- [ ] **Effet "transcript animé"** : rejouer en CSS/JS un vrai échange déjà eu (texte réel, pas inventé), avec apparition progressive façon frappe — donne un effet démo vivant sans backend ni clé API exposée.
- [ ] Explicitement exclu : chat live embarqué dans la page (nécessiterait un backend proxy + gestion de coût/abus — hors scope pour une page de démo statique).
