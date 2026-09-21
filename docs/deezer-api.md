# API Deezer — Documentation de référence pour le MCP

> Toutes les réponses ci-dessous ont été vérifiées en direct sur `api.deezer.com` (2026-09-20), pas recopiées depuis la doc officielle qui est difficile à scraper (contenu derrière du JS/login).

## 1. Généralités

| | |
|---|---|
| **Base URL** | `https://api.deezer.com` |
| **Format** | JSON par défaut (XML possible via `output=xml`, non utilisé ici) |
| **Auth** | Aucune pour les endpoints publics en lecture (search, track, album, artist, playlist, chart, genre) — pas de clé API à gérer |
| **Auth OAuth** | Existe pour les actions écrivant sur un compte utilisateur (favoris, playlists perso) — **hors scope** du projet, on ne fait que de la lecture publique |
| **Rate limit** | ~50 requêtes / 5 secondes par IP. Au-delà : erreur avec `code: 4` (`Quota limit exceeded`) |
| **Pays** | Le catalogue est filtré par pays (géo-restriction de licence). L'IP du serveur déterminera le catalogue vu — un titre disponible en France peut être absent d'un autre pays (`available_countries` sur l'objet track) |

## 2. Format des réponses

### Succès (objet unique)
Renvoie directement l'objet demandé (`GET /track/3135556` → objet track).

### Succès (liste)
```json
{
  "data": [ /* objets */ ],
  "total": 182,
  "next": "https://api.deezer.com/search?q=daft%20punk&limit=1&index=1"
}
```
- `total` : nombre total de résultats disponibles (pas seulement dans cette page)
- `next` : URL de la page suivante, **absente si c'est la dernière page**
- Pagination : paramètres `index` (offset, défaut 0) et `limit` (défaut 25, max observé ~100)

### Erreur
```json
{
  "error": {
    "type": "DataException",
    "message": "no data",
    "code": 800
  }
}
```
Codes rencontrés / connus :
| Code | Type | Signification |
|---|---|---|
| `800` | `DataException` | Ressource introuvable (ex: ID inexistant) |
| `4` | — | `Quota limit exceeded` — trop de requêtes trop vite |

⚠️ Point important pour le MCP : Deezer renvoie **toujours un HTTP 200**, même en cas d'erreur logique. Il faut donc systématiquement vérifier la présence d'une clé `"error"` dans le JSON, pas se fier au status code HTTP.

## 3. Endpoints utiles pour le MCP

### 3.1 Recherche — `GET /search`

Recherche libre multi-critères (mélange tracks/albums/artistes selon le texte).

```
GET /search?q={texte}&limit={n}&index={offset}
```

Sous-endpoints pour cibler un type précis :
| Endpoint | Renvoie |
|---|---|
| `/search` | résultats mixtes, orientés tracks |
| `/search/track` | tracks uniquement |
| `/search/album` | albums uniquement |
| `/search/artist` | artistes uniquement |
| `/search/playlist` | playlists publiques |

**Recherche avancée** (filtres par champ) — syntaxe documentée : `artist:"..."`, `album:"..."`, `track:"..."`.

Testé en direct :
- Un seul filtre fonctionne bien : `q=artist:"Eminem"` ✅, `q=track:"Not Afraid"` ✅, `q=album:"Discovery"` ✅
- Combiner deux filtres est **peu fiable** : `q=artist:"Daft Punk" track:"One More Time"` → `total: 0` alors que chaque filtre pris seul fonctionne. Un seul cas de combinaison a fonctionné dans mes tests (`artist:eminem track:"Not Afraid"`, sans guillemets sur l'artiste). 
- **Recommandation pour le MCP** : exposer un seul filtre à la fois (ou la recherche texte libre), et documenter cette limite plutôt que de promettre une recherche multi-champs fiable.

Exemple de réponse (`/search?q=eminem&limit=1`) : voir §4 (objet Track).

### 3.2 Track — `GET /track/{id}`

Champs clés :
| Champ | Type | Description |
|---|---|---|
| `id` | int | ID Deezer |
| `title` | string | Titre |
| `duration` | int | Durée en secondes |
| `preview` | string (URL) | **Lien MP3 direct, extrait de 30s, aucune auth requise, expire (`hdnea=exp=...` dans le token de l'URL)** — c'est ce champ qui nous intéresse pour l'écoute |
| `link` | string | Page Deezer web du titre |
| `rank` | int | Popularité (indicateur interne Deezer) |
| `explicit_lyrics` | bool | Contenu explicite ou non |
| `available_countries` | array | Codes pays où le titre est streamable |
| `artist` | object | Sous-objet artiste (id, name, link, images) |
| `album` | object | Sous-objet album (id, title, cover, tracklist) |
| `contributors` | array | Tous les artistes crédités (featurings inclus) |

⚠️ **Le champ `preview` a une URL signée qui expire** (paramètre `exp=` visible dans le token `hdnea`). Ne pas mettre ces URLs en cache long terme côté MCP — les récupérer à la demande.

### 3.3 Album — `GET /album/{id}`

Champs clés : `id`, `title`, `cover` (+ variantes `_small/_medium/_big/_xl`), `release_date`, `nb_tracks`, `duration` (total en secondes), `genres.data[]`, `artist`, `tracks.data[]` (liste paginée des titres, chacun avec son `preview`).

Sous-endpoint dédié pour la tracklist paginée : `GET /album/{id}/tracks?limit=&index=`

### 3.4 Artist — `GET /artist/{id}`

Champs clés : `id`, `name`, `nb_album`, `nb_fan`, `picture_*`, `tracklist` (URL vers le top titres).

Sous-endpoints utiles :
| Endpoint | Renvoie |
|---|---|
| `/artist/{id}/top?limit=` | Titres les plus populaires de l'artiste (chacun avec `preview`) |
| `/artist/{id}/albums` | Discographie |
| `/artist/{id}/related` | Artistes similaires |

### 3.5 Playlist — `GET /playlist/{id}`

Champs clés : `id`, `title`, `description`, `public` (les playlists privées ne sont pas accessibles sans OAuth), `nb_tracks`, `fans`, `tracks.data[]`.

### 3.6 Chart / Genre (bonus, découverte de catalogue)

- `GET /chart` → top tracks/albums/artists/playlists du moment (global ou par genre via `/chart/{genre_id}`)
- `GET /genre` → liste des genres disponibles (id + nom), utile pour filtrer les charts

## 4. Exemple complet vérifié — objet Track

```json
{
  "id": 3135556,
  "title": "Harder, Better, Faster, Stronger",
  "duration": 226,
  "release_date": "2001-03-12",
  "explicit_lyrics": false,
  "preview": "https://cdnt-preview.dzcdn.net/api/1/1/6/a/2/0/6a2c0a5670afe821e08fc5154909534a.mp3?hdnea=exp=1789922405~acl=...~hmac=...",
  "available_countries": ["FR", "US", "GB", "..."],
  "artist": {
    "id": 27,
    "name": "Daft Punk",
    "link": "https://www.deezer.com/artist/27",
    "picture_medium": "https://cdn-images.dzcdn.net/images/artist/.../250x250-000000-80-0-0.jpg",
    "tracklist": "https://api.deezer.com/artist/27/top?limit=50"
  },
  "album": {
    "id": 302127,
    "title": "Discovery",
    "cover_medium": "https://cdn-images.dzcdn.net/images/cover/.../250x250-000000-80-0-0.jpg",
    "tracklist": "https://api.deezer.com/album/302127/tracks"
  }
}
```

## 5. Ce que ça implique pour le design du MCP

- **Pas de clé API/secret à stocker** → pas de gestion de credentials côté serveur MCP pour les endpoints de lecture publique.
- **Gérer le rate limit (50 req / 5s)** : prévoir un throttling léger côté serveur si plusieurs tool calls rapides (ex: une recherche puis récupération de plusieurs previews) — sinon risque de `code: 4`.
- **Toujours checker la clé `"error"` dans le JSON**, jamais se fier au status HTTP (toujours 200).
- **Ne pas cacher les URLs `preview`** trop longtemps (elles expirent), les resservir "fraîches" à chaque appel de tool.
- **Filtrer par pays si besoin** via `available_countries`, pertinent si on veut prévenir l'utilisateur qu'un titre pourrait ne pas être lisible partout.
- Outils MCP naturels à exposer : `search_tracks`, `get_track`, `get_album`, `get_artist_top_tracks`, `get_playlist` — chacun un wrapper mince autour d'un endpoint, avec le `preview` remonté explicitement pour l'écoute côté client (Artifact `<audio>` ou lien direct).
- Deux tools supplémentaires implémentés au-delà du mapping 1 endpoint = 1 tool : `get_artist_profile` (composite : `/artist/{id}` + `/artist/{id}/top` + `/artist/{id}/related` en un seul appel) et le duo `list_genres`/`get_chart_tracks` (`/genre` + `/chart` + `/chart/{genre_id}`) pour laisser le modèle composer une playlist par ambiance sans NLP côté serveur.

## Sources
- [Deezer API Rate limit · Issue #6 · BackInBash/DeezerSync](https://github.com/BackInBash/DeezerSync/issues/6)
- [Deezer - Error Code 4, Quota limit Exceeded](https://rapidapi.com/deezerdevs/api/Deezer/discussions/21000)
- Endpoints `api.deezer.com` interrogés directement (search, track, album, artist, playlist, chart, genre, infos) le 2026-09-20.
