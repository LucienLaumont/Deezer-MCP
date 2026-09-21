"""Constructeurs de payloads Deezer bruts (format API), pour les tests.

Les valeurs par défaut reprennent l'exemple vérifié en direct dans docs/deezer-api.md.
"""


def make_track(**overrides) -> dict:
    data = {
        "id": 3135556,
        "title": "Harder, Better, Faster, Stronger",
        "duration": 226,
        "preview": "https://cdnt-preview.dzcdn.net/api/1/x.mp3?hdnea=exp=123",
        "link": "https://www.deezer.com/track/3135556",
        "artist": {"id": 27, "name": "Daft Punk"},
        "album": {"id": 302127, "title": "Discovery"},
    }
    data.update(overrides)
    return data


def make_artist(**overrides) -> dict:
    data = {
        "id": 27,
        "name": "Daft Punk",
        "nb_fan": 5208863,
        "nb_album": 39,
        "picture_medium": "https://cdn-images.dzcdn.net/images/artist/x/250x250.jpg",
        "link": "https://www.deezer.com/artist/27",
    }
    data.update(overrides)
    return data


def make_album(**overrides) -> dict:
    data = {
        "id": 302127,
        "title": "Discovery",
        "artist": {"name": "Daft Punk"},
        "release_date": "2001-03-12",
        "nb_tracks": 14,
        "cover_medium": "https://cdn-images.dzcdn.net/images/cover/x/250x250.jpg",
        "link": "https://www.deezer.com/album/302127",
    }
    data.update(overrides)
    return data


def make_genre(**overrides) -> dict:
    data = {
        "id": 132,
        "name": "Pop",
        "picture_medium": "https://cdn-images.dzcdn.net/images/misc/x/250x250.jpg",
    }
    data.update(overrides)
    return data
