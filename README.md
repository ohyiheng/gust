# Spotify Autotagger

A Python CLI utility to automatically tag music files using metadata retrieved from Spotify.

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

### Configuration

1. Rename `.env.example` to `.env`:
2. Fill in your Spotify API credentials `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` in the `.env` file.

### Usage

Run the script from the command line:
- Windows:
    ```powershell
    python main.py
    ```
- Unix-based systems:
    ```sh
    python3 main.py
    ```

Follow the prompts to apply tags automatically or select tags interactively.

## Roadmap

- [x] Search and fetch tracks from Spotify
- [x] Add an option to choose from a list of query results
- [x] Retrieve album images
- [ ] CLI parameter to specify path to music files
- [ ] Replay gain tags?
- [ ] Allow users to customize the behavior of the program using a config file
- [ ] Enable users to select the tags they want to write