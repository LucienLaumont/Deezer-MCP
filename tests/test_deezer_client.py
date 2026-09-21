import httpx
import pytest
from httpx import Response

from deezer_mcp.deezer_client import DeezerAPIError
from tests.conftest import DEEZER_BASE_URL
from tests.factories import make_album, make_artist, make_genre, make_track

BASE = DEEZER_BASE_URL


# --- search ------------------------------------------------------------------


async def test_search_tracks_shapes_results(client, respx_mock):
    respx_mock.get(f"{BASE}/search/track").mock(
        return_value=Response(200, json={"data": [make_track()], "total": 1})
    )

    results = await client.search_tracks("daft punk", limit=5)

    assert results == [
        {
            "id": 3135556,
            "title": "Harder, Better, Faster, Stronger",
            "artist": "Daft Punk",
            "featured_artists": None,
            "album": "Discovery",
            "album_id": 302127,
            "duration": 226,
            "preview": "https://cdnt-preview.dzcdn.net/api/1/x.mp3?hdnea=exp=123",
            "link": "https://www.deezer.com/track/3135556",
        }
    ]


async def test_search_tracks_passes_query_and_limit(client, respx_mock):
    route = respx_mock.get(f"{BASE}/search/track").mock(
        return_value=Response(200, json={"data": [], "total": 0})
    )

    await client.search_tracks("eminem", limit=3)

    params = route.calls.last.request.url.params
    assert params["q"] == "eminem"
    assert params["limit"] == "3"


async def test_search_albums_shapes_results(client, respx_mock):
    respx_mock.get(f"{BASE}/search/album").mock(
        return_value=Response(200, json={"data": [make_album()], "total": 1})
    )

    results = await client.search_albums("discovery", limit=5)

    assert results == [
        {
            "id": 302127,
            "title": "Discovery",
            "artist": "Daft Punk",
            "release_date": "2001-03-12",
            "nb_tracks": 14,
            "cover": "https://cdn-images.dzcdn.net/images/cover/x/250x250.jpg",
            "link": "https://www.deezer.com/album/302127",
        }
    ]


async def test_search_artists_shapes_results(client, respx_mock):
    respx_mock.get(f"{BASE}/search/artist").mock(
        return_value=Response(200, json={"data": [make_artist()], "total": 1})
    )

    results = await client.search_artists("daft punk", limit=5)

    assert results == [
        {
            "id": 27,
            "name": "Daft Punk",
            "nb_fan": 5208863,
            "nb_album": 39,
            "picture": "https://cdn-images.dzcdn.net/images/artist/x/250x250.jpg",
            "link": "https://www.deezer.com/artist/27",
        }
    ]


# --- track / album / featured_artists -----------------------------------------


async def test_get_track_computes_featured_artists_from_contributors(
    client, respx_mock
):
    raw = make_track(
        contributors=[{"name": "Daft Punk"}, {"name": "Pharrell Williams"}]
    )
    respx_mock.get(f"{BASE}/track/3135556").mock(return_value=Response(200, json=raw))

    result = await client.get_track(3135556)

    assert result["featured_artists"] == ["Pharrell Williams"]


async def test_get_track_featured_artists_is_none_when_no_contributors_field(
    client, respx_mock
):
    # /search/track et la tracklist de /album/{id} n'ont pas de "contributors" :
    # featured_artists doit rester None (info non disponible), pas [] (aucun featuring).
    raw = make_track()
    respx_mock.get(f"{BASE}/track/3135556").mock(return_value=Response(200, json=raw))

    result = await client.get_track(3135556)

    assert result["featured_artists"] is None


async def test_get_track_featured_artists_empty_list_when_contributors_is_solo(
    client, respx_mock
):
    raw = make_track(contributors=[{"name": "Daft Punk"}])
    respx_mock.get(f"{BASE}/track/3135556").mock(return_value=Response(200, json=raw))

    result = await client.get_track(3135556)

    assert result["featured_artists"] == []


async def test_get_album_includes_shaped_tracklist(client, respx_mock):
    raw = make_album()
    raw["tracks"] = {"data": [make_track()]}
    respx_mock.get(f"{BASE}/album/302127").mock(return_value=Response(200, json=raw))

    result = await client.get_album(302127)

    assert result["title"] == "Discovery"
    assert len(result["tracks"]) == 1
    assert result["tracks"][0]["title"] == "Harder, Better, Faster, Stronger"


async def test_get_artist_top_tracks(client, respx_mock):
    respx_mock.get(f"{BASE}/artist/27/top").mock(
        return_value=Response(200, json={"data": [make_track()]})
    )

    results = await client.get_artist_top_tracks(27, limit=1)

    assert results[0]["artist"] == "Daft Punk"


# --- erreurs -------------------------------------------------------------------


async def test_error_payload_raises_deezer_api_error(client, respx_mock):
    respx_mock.get(f"{BASE}/track/999").mock(
        return_value=Response(
            200,
            json={
                "error": {"type": "DataException", "message": "no data", "code": 800}
            },
        )
    )

    with pytest.raises(DeezerAPIError, match="no data"):
        await client.get_track(999)


async def test_http_status_error_raises_deezer_api_error(client, respx_mock):
    respx_mock.get(f"{BASE}/track/1").mock(return_value=Response(500))

    with pytest.raises(DeezerAPIError):
        await client.get_track(1)


async def test_network_error_raises_deezer_api_error(client, respx_mock):
    respx_mock.get(f"{BASE}/track/1").mock(side_effect=httpx.ConnectError("boom"))

    with pytest.raises(DeezerAPIError):
        await client.get_track(1)


# --- fiche artiste enrichie (composite) -----------------------------------------


async def test_get_artist(client, respx_mock):
    respx_mock.get(f"{BASE}/artist/27").mock(
        return_value=Response(200, json=make_artist())
    )

    result = await client.get_artist(27)

    assert result == {
        "id": 27,
        "name": "Daft Punk",
        "nb_fan": 5208863,
        "nb_album": 39,
        "picture": "https://cdn-images.dzcdn.net/images/artist/x/250x250.jpg",
        "link": "https://www.deezer.com/artist/27",
    }


async def test_get_related_artists(client, respx_mock):
    respx_mock.get(f"{BASE}/artist/27/related").mock(
        return_value=Response(
            200, json={"data": [make_artist(id=6404, name="Justice")]}
        )
    )

    results = await client.get_related_artists(27, limit=5)

    assert results[0]["name"] == "Justice"


async def test_get_artist_profile_combines_the_three_calls(client, respx_mock):
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

    profile = await client.get_artist_profile(27, top_tracks_limit=10, related_limit=5)

    assert profile["artist"]["name"] == "Daft Punk"
    assert profile["top_tracks"][0]["title"] == "Harder, Better, Faster, Stronger"
    assert profile["related_artists"][0]["name"] == "Justice"


# --- genres / chart (playlist par ambiance) -------------------------------------


async def test_get_genres(client, respx_mock):
    respx_mock.get(f"{BASE}/genre").mock(
        return_value=Response(
            200,
            json={
                "data": [make_genre(id=0, name="Tous"), make_genre(id=132, name="Pop")]
            },
        )
    )

    genres = await client.get_genres()

    assert genres == [
        {
            "id": 0,
            "name": "Tous",
            "picture": "https://cdn-images.dzcdn.net/images/misc/x/250x250.jpg",
        },
        {
            "id": 132,
            "name": "Pop",
            "picture": "https://cdn-images.dzcdn.net/images/misc/x/250x250.jpg",
        },
    ]


async def test_get_chart_tracks_global_hits_chart_endpoint(client, respx_mock):
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

    results = await client.get_chart_tracks(limit=10)

    assert route.called
    assert len(results) == 1


async def test_get_chart_tracks_with_genre_hits_scoped_endpoint(client, respx_mock):
    route = respx_mock.get(f"{BASE}/chart/132").mock(
        return_value=Response(
            200,
            json={
                "tracks": {"data": [make_track(id=1), make_track(id=2)]},
                "albums": {},
                "artists": {},
                "playlists": {},
            },
        )
    )

    results = await client.get_chart_tracks(genre_id=132, limit=1)

    assert route.called
    # Slicing défensif côté client : même si l'API renvoie plus que `limit`.
    assert len(results) == 1
