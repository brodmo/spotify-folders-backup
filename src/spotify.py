import spotipy
from spotipy.oauth2 import SpotifyPKCE

from model import Album, LikedSongs, Playlist, Song, SongRecord


# this is much simpler for the user than providing their own developer credentials
# however, to enable public use, I would need to submit an extension request to Spotify
# probably won't happen, since
# - "we will not grant a quota extension for [...] hobby projects"
#   (I might be misinterpreting this one, there are many "hobby projects" with an extensions
#   such as https://github.com/watsonbox/exportify, https://github.com/secuvera/SpotMyBackup --
#   where is the line between hobby project and open source?)
# - "metadata [must be] attributed with the Spotify logo" (how would I do this in a text file??)
# - "the app name or URL [must not] start with the word “spot”
#   or have similar sound or spelling to Spotify" (how is anyone supposed to find it then?)
# last one is probably a dealbreaker since I want a descriptive name
_client_id = '6c83d30d576d4bcc93a609eef10b9344'
_redirect_uri = 'http://localhost:8888/callback'
_auth = SpotifyPKCE(client_id=_client_id, redirect_uri=_redirect_uri, scope='user-library-read')
_sp = spotipy.Spotify(_auth.get_access_token())


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
