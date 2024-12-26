from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml


def _escape_string(string: str) -> str:
    def clean_char(char: str) -> str:
        if char.isalnum() or char in " ()_-.,":
            return char
        return {"$": "S", "@": "a"}.get(char, "")

    return "".join(map(clean_char, string))


@dataclass
class SongCollection(ABC):
    @abstractmethod
    def write(self, directory: Path):
        pass


@dataclass
class Folder(SongCollection):
    name: str
    contents: list[SongCollection]

    def write(self, directory: Path):
        my_dir = directory / _escape_string(self.name)
        my_dir.mkdir(exist_ok=True)
        for content in self.contents:
            content.write(my_dir)


@dataclass
class SongRecord(SongCollection, ABC):
    @abstractmethod
    def _file_name(self) -> str:
        raise NotImplementedError

    def write(self, directory: Path):
        path = (directory / _escape_string(self._file_name())).with_suffix(".yaml")
        with path.open("w+", encoding="UTF-8") as file:
            yaml.dump(asdict(self), file, sort_keys=False, allow_unicode=True)


@dataclass
class Song:
    uid: str
    name: str
    artist: str


@dataclass
class LikedSongs(SongRecord):
    songs: list[Song]

    def _file_name(self) -> str:
        return "Liked Songs"


@dataclass
class Playlist(SongRecord):
    uid: str
    name: str
    owner_id: str
    songs: list[Song]

    def _file_name(self) -> str:
        return self.name.replace("-", "")


@dataclass
class Album(SongRecord):
    uid: str
    artist: str
    name: str

    def _file_name(self) -> str:
        return f"{self.artist} - {self.name}"
