# Spotify Autotagger

A Python CLI utility to automatically tag music files using metadata retrieved from Spotify. Very much in development, expect bugs and breaking changes.

## Features

- Automatically fetches and applies the following metadata to music files:
  - Track Title
  - Artist(s)
  - Album Title
  - Album Artist
  - Release Date
  - Track Number
  - Total Tracks
  - Disc Number
  - Total Discs
- Automatically fetches and embed album cover into the files
- Supports Vorbis Comments and ID3 tags.
- Interactive selection, an option to choose from a list of query results to ensure the correct metadata is applied.

## Getting Started

### Prerequisites

- Python 3.6 or later
- `pip` for installing dependencies
- A [Spotify Developer](https://developer.spotify.com) account to obtain API credentials

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourgithubusername/spotify-autotagger.git
   ```
2. Navigate to the cloned directory:
   ```sh
   cd spotify-autotagger
   ```
3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Obtaining Spotify API Credentials

1. Create a new application on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/create).
2. Fill in **App name**, **App description** with any suitable values.
3. Spotify requires **Redirect URIs** to be added, we don't need it as we're only using the Client Credentials Flow, so just use any url (e.g. `http://localhost:8080`).
4. Select **Web API** for the API type.
5. Once the application is created, go to the application's settings to see your **Client ID** and **Client Secret**.
6. Copy `.env.example` and rename it to `.env`.
7. Fill in your `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` in the `.env` file.

## Usage

Run the script from the command line:
- Windows:
    ```powershell
    python spotify-autotagger.py -p "path/to/music/files"
    ```
- Unix-based systems:
    ```sh
    python3 spotify-autotagger.py -p "path/to/music/files"
    ```

Follow the prompts to apply tags automatically or select tags interactively.

## Updating

To update the program, pull the latest changes from the repository:
```sh
cd spotify-autotagger
git pull 
```

## Roadmap

- [x] Search and fetch tracks from Spotify
- [x] Add an option to choose from a list of query results
- [x] Retrieve album images
- [ ] CLI parameters to customise the tagging process
- [ ] Cache Spotify access token
- [ ] Replay gain tags?
- [ ] Enable users to select the tags they want to write