## Spotify Folder Backup

A small utility to backup all your Spotify playlists including the folder structure.
As the Spotify API does not support folders, the folder structure is reconstructed from the Spotify cache with [spotify‑folders](https://github.com/mikez/spotify-folders)
(all credit to [mikez](https://github.com/mikez)).

Playlists are automatically resolved to albums where appropriate.
In this case, the individual tracks are not included in the backup.

### Usage
1. Clear Spotify cache in Spotify settings
2. Add Spotify Web API credentials to `credentials.yaml`
3. (Optional) To specify a custom cache directory, account, or folder,
manually create `folders.json` with [spotify‑folders](https://github.com/mikez/spotify-folders).
Otherwise it can be created automatically
4. Install dependencies with `pip install -r requirements.txt`
5. Run with `python src/main.py`
6. The mirrored folder structure is written to `Backup`
