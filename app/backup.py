import json
import stat
import subprocess
import sys
from pathlib import Path

import requests
from spotipy.exceptions import SpotifyException
from tqdm import tqdm

from app.model import Folder, SongCollection
from app.spotify import get_liked_songs, get_song_record


_here = Path(__file__).parent
_folders_json_path = _here.parent / "folders.json"
_root = _here.parent / "Backup"


def _write_folders_json():
    folders_script_url = (
        "https://raw.githubusercontent.com/mikez/spotify-folders/master/folders.py"
    )
    response = requests.get(folders_script_url)
    if not response.ok:
        raise requests.RequestException(
            f"could not get spotifyfolders script from GitHub, reason:\n{response.text}"
        )
    folders_script_path = _here / "folders.py"
    folders_script_path.write_text(response.text)
    folders_script_path.chmod(folders_script_path.stat().st_mode | stat.S_IEXEC)
    result = subprocess.run([sys.executable, folders_script_path], capture_output=True)
    if result.stderr:
        if b"PermissionError" in result.stderr:
            raise PermissionError("fully close Spotify (Alt+F4)")
        else:
            raise RuntimeError(
                f"spotifyfolders script failed, reason:\n{result.stderr}"
            )
    folders_json = json.dumps(json.loads(result.stdout), indent=4)
    _folders_json_path.write_text(folders_json)


def _wrap(data: dict, progress) -> SongCollection | None:
    if data["type"] == "folder":
        contents = [
            wrapped
            for child in data["children"]
            if (wrapped := _wrap(child, progress)) is not None
        ]
        return Folder(data["name"], contents)
    try:
        record = get_song_record(data["uri"])
    except SpotifyException as error:
        # Skip algorithmic playlists
        if error.http_status != 404:
            raise
        record = None
    progress.update(1)
    return record


def _count_playlists(data: dict) -> int:
    if data["type"] == "folder":
        return sum(_count_playlists(child) for child in data["children"])
    return 1


def backup():
    tqdm.write("Reading Spotify folder structure…", file=sys.stderr)
    if _folders_json_path.exists():
        _folders_json_path.unlink()
    _write_folders_json()
    folders_data = json.loads(_folders_json_path.read_text())
    _root.mkdir(exist_ok=True)
    get_liked_songs().write(_root)
    total = _count_playlists(folders_data)
    with tqdm(total=total, desc="Playlists", unit="playlists") as progress:
        for child in folders_data["children"]:
            wrapped = _wrap(child, progress)
            if wrapped is not None:
                wrapped.write(_root)
    tqdm.write("Backup Complete", file=sys.stderr)
