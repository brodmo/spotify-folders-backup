import json
import stat
import subprocess
import sys
from pathlib import Path

import requests

from model import Folder, SongCollection
from spotify import get_liked_songs, get_song_record


_here = Path(__file__).parent
_folders_json_path = _here.parent / 'folders.json'
_root = _here.parent / 'Backup'


def _write_folders_json():
    folders_script_url = 'https://raw.githubusercontent.com/mikez/spotify-folders/master/folders.py'
    response = requests.get(folders_script_url)
    if not response.ok:
        raise requests.RequestException(f'could not get spotifyfolders script from GitHub, reason:\n{response.text}')
    assert response.ok, 'could not get spotfiyfolders script'
    folders_script_path = _here / 'folders.py'
    folders_script_path.write_text(response.text)
    folders_script_path.chmod(folders_script_path.stat().st_mode | stat.S_IEXEC)
    result = subprocess.run([sys.executable, folders_script_path], capture_output=True)
    if result.stderr:
        if b'PermissionError' in result.stderr:
            raise PermissionError('fully close Spotify (Alt+F4)')
        else:
            raise RuntimeError(f'spotifyfolders script failed, reason:\n{result.stderr}')
    folders_json = json.dumps(json.loads(result.stdout), indent=4)
    _folders_json_path.write_text(folders_json)


def _wrap(data: dict) -> SongCollection:
    return (
        Folder(data['name'], [_wrap(child) for child in data['children']])
        if data['type'] == 'folder' else get_song_record(data['uri'])
    )


def main():
    if not _folders_json_path.exists():
        _write_folders_json()
    folders_data = json.loads(_folders_json_path.read_text())
    _root.mkdir(exist_ok=True)
    get_liked_songs().write(_root)
    for child in folders_data['children']:
        wrapped = _wrap(child)
        wrapped.write(_root)


if __name__ == '__main__':
    main()
