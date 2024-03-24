import json
import stat
import subprocess
from pathlib import Path

import requests

from model import Folder, SongCollection
from spotify import get_liked_songs, get_song_record


here = Path(__file__).parent
folders_json_path = here.parent / 'folders.json'
root = here.parent / 'Backup'


def escape_string(string: str):
    def clean_char(char: str):
        if char.isalnum() or char in ' ()_-.,':
            return char
        try:
            return {
                '$': 'S',
                '@': 'a'
            }[char]
        except KeyError:
            return ''
    return ''.join(map(clean_char, string))


def write_folders_json():
    folders_script_url = 'https://raw.githubusercontent.com/mikez/spotify-folders/master/folders.py'
    response = requests.get(folders_script_url)
    assert response.ok, 'could not get spotfiyfolders script'
    folders_script_path = here / 'folders.py'
    folders_script_path.write_text(response.text)
    folders_script_path.chmod(folders_script_path.stat().st_mode | stat.S_IEXEC)
    folders_data = subprocess.run(folders_script_path, capture_output=True).stdout
    folders_data = json.dumps(json.loads(folders_data), indent=4)
    folders_json_path.write_text(folders_data)


def wrap(data: dict) -> SongCollection:
    if data['type'] == 'folder':
        contents = [wrap(child) for child in data['children']]
        return Folder(data['name'], contents)
    else:
        return get_song_record(data['uri'])


def main():
    if not folders_json_path.exists():
        write_folders_json()
    folders_data = json.loads(folders_json_path.read_text())
    root.mkdir(exist_ok=True)
    get_liked_songs().write(root)
    for child in folders_data['children']:
        wrapped = wrap(child)
        wrapped.write(root)


if __name__ == '__main__':
    main()
