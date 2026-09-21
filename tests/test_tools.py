"""Tests des tools MCP eux-mêmes (enregistrement + comportement), via un appel
`mcp.call_tool()` en mémoire plutôt qu'un vrai serveur/transport.

Le détail du shaping des données Deezer (contributors, cover, etc.) est déjà couvert
par tests/test_deezer_client.py : ici on vérifie que chaque tool est bien câblé au
client, et surtout la logique propre aux tools composites (résolution par nom,
validation des paramètres) qui n'existe pas au niveau du client.
"""

import json

import pytest
from httpx import Response
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import UnexpectedToolError

from deezer_mcp.deezer_client import DeezerClient
from deezer_mcp.tools import albums, artists, discovery, search, tracks
from tests.conftest import DEEZER_BASE_URL
from tests.factories import make_album, make_artist, make_genre, make_track

BASE = DEEZER_BASE_URL

ALL_TOOL_NAMES = {
    "search_tracks",
    "search_albums",
    "search_artists",
    "get_track",
    "get_album",
    "get_artist_top_tracks",
    "get_artist_profile",
    "list_genres",
    "get_chart_tracks",
}


@pytest.fixture
async def mcp():
    server = MCPServer("test-deezer-mcp")
    client = DeezerClient()
    search.register(server, client)
    tracks.register(server, client)
    albums.register(server, client)
    artists.register(server, client)
    discovery.register(server, client)
    yield server
    await client.close()


def payload(result):
    """Extrait la valeur de retour d'un CallToolResult.

    Les tools qui renvoient une liste ont `structured_content = {"result": [...]}`
    (un TextContent par item) ; ceux qui renvoient un dict n'ont pas de
    structured_content, la valeur est alors le JSON du seul bloc `content`.
    """
    if result.structured_content is not None:
        return result.structured_content.get("result", result.structured_content)
    return json.loads(result.content[0].text)


async def test_all_tools_registered(mcp):
    names = {t.name for t in await mcp.list_tools()}
    assert names == ALL_TOOL_NAMES


async def test_search_tracks_tool_delegates_to_client(mcp, respx_mock):
    respx_mock.get(f"{BASE}/search/track").mock(
        return_value=Response(200, json={"data": [make_track()], "total": 1})
    )

    result = await mcp.call_tool("search_tracks", {"query": "daft punk"})

    assert not result.is_error
    assert payload(result)[0]["title"] == "Harder, Better, Faster, Stronger"


async def test_search_albums_tool_delegates_to_client(mcp, respx_mock):
    respx_mock.get(f"{BASE}/search/album").mock(
        return_value=Response(200, json={"data": [make_album()], "total": 1})
    )

    result = await mcp.call_tool("search_albums", {"query": "discovery"})

    assert payload(result)[0]["title"] == "Discovery"


async def test_search_artists_tool_delegates_to_client(mcp, respx_mock):
    respx_mock.get(f"{BASE}/search/artist").mock(
        return_value=Response(200, json={"data": [make_artist()], "total": 1})
    )

    result = await mcp.call_tool("search_artists", {"query": "daft punk"})

    assert payload(result)[0]["name"] == "Daft Punk"


async def test_get_track_tool_delegates_to_client(mcp, respx_mock):
    respx_mock.get(f"{BASE}/track/3135556").mock(
        return_value=Response(200, json=make_track())
    )

    result = await mcp.call_tool("get_track", {"track_id": 3135556})

    assert payload(result)["id"] == 3135556


async def test_get_album_tool_delegates_to_client(mcp, respx_mock):
    raw = make_album()
    raw["tracks"] = {"data": [make_track()]}
    respx_mock.get(f"{BASE}/album/302127").mock(return_value=Response(200, json=raw))

    result = await mcp.call_tool("get_album", {"album_id": 302127})

    assert len(payload(result)["tracks"]) == 1


async def test_get_artist_top_tracks_tool_delegates_to_client(mcp, respx_mock):
    respx_mock.get(f"{BASE}/artist/27/top").mock(
        return_value=Response(200, json={"data": [make_track()]})
    )

    result = await mcp.call_tool("get_artist_top_tracks", {"artist_id": 27})

    assert payload(result)[0]["artist"] == "Daft Punk"


# --- get_artist_profile (composite) ---------------------------------------------


async def test_get_artist_profile_by_id(mcp, respx_mock):
    respx_mock.get(f"{BASE}/artist/27").mock(
        return_value=Response(200, json=make_artist())
    )
    respx_mock.get(f"{BASE}/artist/27/top").mock(
        return_value=Response(200, json={"data": [make_track()]})
    )
    respx_mock.get(f"{BASE}/artist/27/related").mock(
        return_value=Response(
            200, json={"data": [make_artist(id=6404, name="Justice")]}
        )
    )

    result = await mcp.call_tool("get_artist_profile", {"artist_id": 27})

    body = payload(result)
    assert body["artist"]["name"] == "Daft Punk"
    assert body["top_tracks"][0]["title"] == "Harder, Better, Faster, Stronger"
    assert body["related_artists"][0]["name"] == "Justice"


async def test_get_artist_profile_by_name_resolves_most_popular_candidate(
    mcp, respx_mock
):
    # Reproduit le cas réel observé sur l'API Deezer : le tri par pertinence de
    # `/search/artist` peut placer un homonyme obscur avant l'artiste populaire
    # recherché (cf. docstring de get_artist_profile). Le tool doit résoudre vers
    # le candidat avec le plus de fans, pas le premier de la liste.
    respx_mock.get(f"{BASE}/search/artist").mock(
        return_value=Response(
            200,
            json={
                "data": [
                    make_artist(id=4333065, name="justice", nb_fan=1030),
                    make_artist(id=6404, name="Justice", nb_fan=808896),
                ],
                "total": 2,
            },
        )
    )
    respx_mock.get(f"{BASE}/artist/6404").mock(
        return_value=Response(200, json=make_artist(id=6404, name="Justice"))
    )
    respx_mock.get(f"{BASE}/artist/6404/top").mock(
        return_value=Response(200, json={"data": [make_track()]})
    )
    respx_mock.get(f"{BASE}/artist/6404/related").mock(
        return_value=Response(200, json={"data": []})
    )

    result = await mcp.call_tool("get_artist_profile", {"artist_name": "Justice"})

    assert payload(result)["artist"]["id"] == 6404


async def test_get_artist_profile_requires_exactly_one_of_id_or_name(mcp):
    with pytest.raises(UnexpectedToolError) as exc_info:
        await mcp.call_tool("get_artist_profile", {})
    assert isinstance(exc_info.value.__cause__, ValueError)

    with pytest.raises(UnexpectedToolError) as exc_info:
        await mcp.call_tool(
            "get_artist_profile", {"artist_id": 27, "artist_name": "Daft Punk"}
        )
    assert isinstance(exc_info.value.__cause__, ValueError)


async def test_get_artist_profile_raises_when_name_not_found(mcp, respx_mock):
    respx_mock.get(f"{BASE}/search/artist").mock(
        return_value=Response(200, json={"data": [], "total": 0})
    )

    with pytest.raises(UnexpectedToolError) as exc_info:
        await mcp.call_tool(
            "get_artist_profile", {"artist_name": "Un Artiste Qui N'existe Pas"}
        )

    assert "Aucun artiste" in str(exc_info.value.__cause__)


# --- playlist par ambiance (list_genres / get_chart_tracks) ---------------------


async def test_list_genres_tool_delegates_to_client(mcp, respx_mock):
    respx_mock.get(f"{BASE}/genre").mock(
        return_value=Response(200, json={"data": [make_genre()]})
    )

    result = await mcp.call_tool("list_genres", {})

    assert payload(result)[0]["name"] == "Pop"


async def test_get_chart_tracks_tool_with_genre_id(mcp, respx_mock):
    respx_mock.get(f"{BASE}/chart/132").mock(
        return_value=Response(
            200,
            json={
                "tracks": {"data": [make_track()]},
                "albums": {},
                "artists": {},
                "playlists": {},
            },
        )
    )

    result = await mcp.call_tool("get_chart_tracks", {"genre_id": 132, "limit": 5})

    assert payload(result)[0]["title"] == "Harder, Better, Faster, Stronger"


async def test_get_chart_tracks_tool_without_genre_id_hits_global_chart(
    mcp, respx_mock
):
    route = respx_mock.get(f"{BASE}/chart").mock(
        return_value=Response(
            200,
            json={
                "tracks": {"data": [make_track()]},
                "albums": {},
                "artists": {},
                "playlists": {},
            },
        )
    )

    result = await mcp.call_tool("get_chart_tracks", {})

    assert route.called
    assert len(payload(result)) == 1
