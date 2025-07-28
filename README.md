# gust - get your songs tagged

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Static Badge](https://img.shields.io/badge/version-0.2.0-blue?style=for-the-badge)


`gust` lets you automatically tag your local music files using metadata from Spotify.

![demo](/static/demo.gif)

<details>
<summary>Interactive mode: </summary>

![demo-interactive](/static/demo-interactive.gif)
</details>

## Features

- Fetch and apply the following metadata to music files:
  - Track Title
  - Artist(s)
  - Album Title
  - Album Artist
  - Release Date
  - Track Number
  - Total Tracks
  - Disc Number
  - Total Discs
- Fetch and embed album cover into the files
- Support MP3, FLAC, OGG and Opus
- Support interactive mode (choose from a list of results)

## Installation

Pre-built binary for Linux is available on the [releases](https://github.com/ohyiheng/gust/releases) page.

NOTE: Spotify API credentials are required. See: [Obtaining Spotify API Credentials](#obtaining-spotify-api-credentials).


## Usage

- `gust tag` - Tag files in current directory in default mode (always choose the first result)
- `gust tag -p ~/Music` - Tag files in "~/Music" directory in default mode
- `gust tag -i` - Tag files in current directory in interactive mode (choose from 5 results)

Use `-h` or `--help` to display help message.

```
usage: gust [-h] {tag,config} ...

get your songs tagged with metadata from Spotify

positional arguments:
  {tag,config}
    tag         tag music files
    config      configure gust

options:
  -h, --help    show this help message and exit
```

```
usage: gust tag [-h] [-p PATH] [-i] [--date-full] [--always-keep-discs]

options:
  -h, --help           show this help message and exit
  -p, --path PATH      specify the path to music files, defaults to the current directory
  -i, --interactive    select tags from query results interactively
  --date-full          use full date instead of just the year
  --always-keep-discs  keep disc tags even if there's only one disc
```

```
usage: gust config [-h] {api,reset} ...

positional arguments:
  {api,reset}
    api        configure spotify's api client id and secret
    reset      reset config file

options:
  -h, --help   show this help message and exit
```

### Obtaining Spotify API Credentials

1. Create a new application on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/create).
2. Fill in *App name*, *App description* with any suitable values.
3. Put any address in *Redirect URIs* (e.g. `http://localhost:8080`).
4. Select *Web API* for the API type.
5. Once the application is created, go to the application's settings to see your *Client ID* and *Client Secret*.

## Roadmap

- [x] Search and fetch tracks from Spotify
- [x] Add an option to choose from a list of query results
- [x] Retrieve album images
- [x] CLI parameters to customise the tagging process
- [ ] Rename files based on metadata
- [ ] Retrieve lyrics using Netease Cloud Music API
- [ ] Replay gain tags?
- [ ] Enable users to select the tags they want to write