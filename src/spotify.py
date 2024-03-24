import spotipy
from spotipy.oauth2 import SpotifyOAuth

from credentials import *
from model import Album, LikedSongs, Playlist, Song


sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=['user-library-read', 'playlist-read-private', 'playlist-read-collaborative']
    )
)


def _get_all_tracks(data):
    items = data['items']
    while data['next']:
        data = sp.next(data)
        items.extend(data['items'])
    return list(filter(bool, (item['track'] for item in items)))


def _get_album_data(items):
    is_album = len(items) >= 3 and len(set(item['album']['id'] for item in items)) == 1
    return items[0]['album'] if is_album else None


def _get_artist(data):
    return ', '.join(artist_data['name'] for artist_data in data['artists'])


def _get_songs(tracks):
    return [
        Song(data['id'], data['name'], _get_artist(data))
        for data in tracks
    ]


def get_liked_songs():
    tracks = _get_all_tracks(sp.current_user_saved_tracks(limit=50))
    return LikedSongs(_get_songs(tracks))


def get_song_record(uri: str):
    data = sp.playlist(uri)
    tracks = _get_all_tracks(data['tracks'])
    album_data = _get_album_data(tracks)
    if album_data:
        return Album(album_data['id'], _get_artist(album_data), album_data['name'])
    else:
        return Playlist(
            data['id'], data['name'],
            data['owner']['id'], _get_songs(tracks)
        )
