from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from yaml import unsafe_load

from model import Album, LikedSongs, Playlist, Song, SongRecord


_credentials_path = Path(__file__).parent.parent / 'credentials.yaml'
_credentials = unsafe_load(_credentials_path.read_text())
_auth = SpotifyOAuth(**_credentials, scope='user-library-read')
_sp = spotipy.Spotify(auth_manager=_auth)


def _get_all_tracks(data) -> list[dict]:
    items = data['items']
    while data['next']:
        data = _sp.next(data)
        items.extend(data['items'])
    return list(filter(bool, (item['track'] for item in items)))


def _get_album_data(items: list[dict]) -> dict:
    is_album = len(items) >= 3 and len(set(item['album']['id'] for item in items)) == 1
    return items[0]['album'] if is_album else None


def _get_artist(data: dict) -> str:
    return ', '.join(artist_data['name'] for artist_data in data['artists'])


def _get_songs(tracks: list[dict]) -> list[Song]:
    return [
        Song(data['id'], data['name'], _get_artist(data))
        for data in tracks
    ]


def get_liked_songs() -> LikedSongs:
    tracks = _get_all_tracks(_sp.current_user_saved_tracks(limit=50))
    return LikedSongs(_get_songs(tracks))


def get_song_record(uri: str) -> SongRecord:
    data = _sp.playlist(uri)
    tracks = _get_all_tracks(data['tracks'])
    album_data = _get_album_data(tracks)
    if album_data:
        return Album(album_data['id'], _get_artist(album_data), album_data['name'])
    else:
        return Playlist(
            data['id'], data['name'],
            data['owner']['id'], _get_songs(tracks)
        )
