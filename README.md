## Spotify Folders Backup

A small utility to backup all your Spotify playlists including the folder structure.
As the Spotify API does not support folders, the folder structure is reconstructed from the Spotify cache with [spotify‑folders](https://github.com/mikez/spotify-folders)
(all credit to [mikez](https://github.com/mikez)).

Playlists are automatically resolved to albums where appropriate.
In this case, the individual tracks are not included in the backup.

### Instructions
1. Prepare Spotify
   1. Clear Spotify cache in Spotify settings
   2. [Windows only] Fully close Spotify (Alt+F4)
2. Prepare script
   1. Add Spotify Web API credentials to `credentials.yaml`
   2. [Optional] Specify a custom cache directory, account, or folder
   by running [spotify‑folders](https://github.com/mikez/spotify-folders) and writing the result to `folders.json`
3. Run script
   1. Install dependencies with `pip install -r requirements.txt`
   2. Run with `python src/main.py`
4. Result can be found in `Backup`
