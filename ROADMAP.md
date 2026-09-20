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

## 5. Idées à discuter avant de s'engager

- [ ] Un tool plus "agentique" combinant plusieurs endpoints en un seul appel (ex: une fiche complète artiste + top titres + albums en une seule réponse), pour illustrer une orchestration côté serveur plutôt que de laisser le modèle enchaîner les appels.
- [ ] Résilience face à du contenu non fiable renvoyé par l'API dans le contexte du modèle (les résultats de recherche Deezer sont du texte libre saisi par des tiers — angle "sécurité des AI tools" pertinent pour un portfolio).
