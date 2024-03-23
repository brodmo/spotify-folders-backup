import os

import requests
from pathlib import Path
import subprocess
import stat
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass


here = Path(__file__).parent
folders_json_path = here.parent / 'folders.json'
root = here.parent / 'root'


def translate_char(char: str):
    if char.isalnum() or char in '()_-.,':
        return char
    try:
        return {
            '$': 'S',
            '@': 'a'
        }[char]
    except KeyError:
        return ''


def translate_string(string: str):
    return ''.join(map(translate_char, string))


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


@dataclass
class Node(ABC):
    @abstractmethod
    def write(self, directory: Path):
        pass


@dataclass
class Folder(Node):
    uri: str
    name: str
    contents: list[Node]

    def write(self, directory: Path):
        my_dir = directory / translate_string(self.name)
        my_dir.mkdir()
        for content in self.contents:
            content.write(my_dir)


@dataclass
class Playlist(Node):
    uri: str

    def write(self, directory: Path):
        my_file = (directory / self.uri).with_suffix('.yaml')
        my_file.write_text('')


def wrap(data: dict) -> Node:
    attributes = {'uri': data['uri']}
    if data['type'] == 'folder':
        attributes |= {
            'name': data['name'],
            'contents': [wrap(child) for child in data['children']]
        }
        return Folder(**attributes)
    else:
        return Playlist(**attributes)


def main():
    if not folders_json_path.exists():
        write_folders_json()
    folders_data = json.loads(folders_json_path.read_text())
    os.mkdir(root)
    for child in folders_data['children']:
        wrapped = wrap(child)
        wrapped.write(root)


if __name__ == '__main__':
    main()
