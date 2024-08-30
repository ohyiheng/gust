# GUST - Get Ur Songs Tagged

GUST is a Python CLI utility to automatically tag your local music files using metadata retrieved from Spotify. It's very early in development so expect bugs and stuff not working here and there.

Automatic tagging:
![showcase](/static/showcase.gif)

Interactive mode:
![interactive](/static/showcase-interactive.gif)

## Table of Contents
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Obtaining Spotify API Credentials](#obtaining-spotify-api-credentials)
- [Usage](#usage)
- [Updating](#updating)
- [Roadmap](#roadmap)

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
- A [Spotify Developer](https://developer.spotify.com) account to obtain API credentials

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/rainmrn/gust.git
   ```
2. Navigate to the cloned directory:
   ```sh
   cd gust
   ```
3. Optionally, create a virtual environment:
   ```sh
   python -m venv venv
   ```
   Activate the virtual environment:
   - Windows:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Unix-based systems:
     ```sh
     source venv/bin/activate
     ```
4. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Obtaining Spotify API Credentials

1. Create a new application on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/create).
2. Fill in **App name**, **App description** with any suitable values.
3. Spotify requires **Redirect URIs** to be added, we don't need it as we're only using the Client Credentials Flow, so just use any url (e.g. `http://localhost:8080`).
4. Select **Web API** for the API type.
5. Once the application is created, go to the application's settings to see your **Client ID** and **Client Secret**.

## Usage

Use `-h` or `--help` to see the available options.

Auto-tag music files in the specified path:
- Windows:
    ```powershell
    python gust.py -p "path/to/music/files"
    ```
- Unix-based systems:
    ```sh
    python3 gust.py -p "path/to/music/files"
    ```

It will ask for your Spotify API credentials the first time you run the script.

## Updating

To update the program, pull the latest changes from the repository:
```sh
cd gust
git pull 
```

## Roadmap

- [x] Search and fetch tracks from Spotify
- [x] Add an option to choose from a list of query results
- [x] Retrieve album images
- [x] CLI parameters to customise the tagging process
- [x] Cache Spotify access token
- [ ] Rename files based on metadata
- [ ] Retrieve lyrics using Netease Cloud Music API
- [ ] Replay gain tags?
- [ ] Enable users to select the tags they want to write