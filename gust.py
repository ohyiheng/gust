import argparse
import json
import mutagen
from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import EasyMP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
import requests
import os
import questionary
from questionary import Style
from base64 import b64encode
import time

def config_reset():
    os.makedirs(app_config_path, exist_ok=True)

    with open(app_config_file_path, 'w') as file:
        file.truncate()
        app_config = {"api": {
            "spotify_client_id": "",
            "spotify_client_secret": "",
            "spotify_access_token": {
                "token": "",
                "expires": ""
            }
        }}
        json.dump(app_config, file, indent=4)


def config_load():
    # Create the config directory if it doesn't exist
    os.makedirs(app_config_path, exist_ok=True)

    # Initialise config if it doesn't exist
    if not os.path.exists(app_config_file_path):
        with open(app_config_file_path, 'w') as file:
            app_config = {"api": {
                "spotify_client_id": "",
                "spotify_client_secret": "",
                "spotify_access_token": {
                    "token": "",
                    "expires": ""
                }
            }}
            json.dump(app_config, file, indent=4)
        
    with open(app_config_file_path, 'r+') as file:
        try:
            app_config = json.load(file)
        except json.JSONDecodeError as e:
            print("Error decoding config.json")
            raise SystemExit(e)
        
        if args.config_api or not app_config['api']['spotify_client_id']:
            client_id = questionary.text("Spotify Client ID:").ask()
            app_config['api']['spotify_client_id'] = client_id
            client_secret = questionary.password("Spotify Client Secret:").ask()
            app_config['api']['spotify_client_secret'] = client_secret

            file.seek(0) # Move the pointer to the beginning of the file
            file.truncate()
            json.dump(app_config, file, indent=4)
            if args.config_api:
                print("API credentials updated.")
                raise SystemExit()

    return app_config

def read_audio_files():
    global path
    audio_items = []

    for dirpath, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(dirpath, file)
            mutagen_file = mutagen.File(file_path, easy=True)
            if isinstance(mutagen_file, FLAC) or isinstance(mutagen_file, OggVorbis) or isinstance(mutagen_file, EasyID3) or isinstance(mutagen_file, EasyMP3):
                audio_items.append(mutagen_file)
                
    if not audio_items:
        print("No audio files found in current directory.")
        path = questionary.path("Enter another path to the music files:", only_directories=True).ask()
        return read_audio_files()

    return audio_items

def get_access_token():
    """
    Retrieves the access token for Spotify's API using the client credentials flow.

    Returns:
        str: The access token for Spotify's API.
    """
    global app_config
    if not app_config['api']['spotify_access_token']['expires'] or float(app_config['api']['spotify_access_token']['expires']) < time.time():
        return refresh_access_token()
    else:    
        return app_config['api']['spotify_access_token']['token']

def refresh_access_token(retry_count=0):
    global app_config
    if retry_count > 3:
        print("Failed to get access token. Please try again later.")
        raise SystemExit()
    
    # Spotify Client ID and Secret environment variables
    spotify_client_id = app_config['api']['spotify_client_id']
    spotify_client_secret = app_config['api']['spotify_client_secret']

    # Spotify Authoization using Client Credentials
    auth_url = "https://accounts.spotify.com/api/token"
    auth_headers = {'Authorization': f"Basic {b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode()).decode('utf-8')}"}
    auth_data = {'grant_type': 'client_credentials'}

    # Getting the access token for Spotify's API
    try:
        auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
        auth_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("HTTP Error: Maybe your Spotify Client ID or Secret is incorrect? Use `--config-api` flag to reconfigure.")
        raise SystemExit(e)
    except requests.exceptions.ConnectionError as e:
        print("Error Connecting:")
        raise SystemExit(e)
    except requests.exceptions.Timeout:
        print("Connection timed out. Retrying in 5 seconds...")
        time.sleep(5)
        get_access_token(retry_count + 1)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    access_token = auth_response.json().get('access_token')

    with open(app_config_file_path, 'r+') as file:
        try:
            app_config = json.load(file)
            file.seek(0) # Move the pointer to the beginning of the file
            file.truncate()
        except json.JSONDecodeError as e:
            print("Error decoding config.json")
            raise SystemExit(e)
        
        app_config['api']['spotify_access_token']['token'] = access_token
        app_config['api']['spotify_access_token']['expires'] = time.time() + 3600
        json.dump(app_config, file, indent=4)
    
    return access_token

def build_query(audio):
    """
    Builds a query string for searching tracks on Spotify based on the audio tags or filename.

    Parameters:
    audio (Audio): A mutagen FileType instance containing audio information including tags and filename.

    Returns:
    str: The query string for searching tracks on Spotify.
    """
    if "title" in audio.tags and "artist" in audio.tags:
        # add album to query if it's available
        if "album" in audio.tags:
            query = f"https://api.spotify.com/v1/search?q={audio.tags['title']}+-+{audio.tags['artist']}+-+{audio.tags['album']}&type=track" 
        # else use title and artist only
        else:
            query = f"https://api.spotify.com/v1/search?q={audio.tags['title']}+-+{audio.tags['artist']}&type=track" 
    # use filename for query as a last resort
    else:
        query = f"https://api.spotify.com/v1/search?q={audio.filename}&type=track"
    return query

def fetch_tracks(query, limit=5):
    """
    Fetches tracks from Spotify API based on the given query.

    Parameters:
        query (str): The search query for tracks.
        limit (int, optional): The maximum number of tracks to fetch. Defaults to 5.

    Returns:
        list or dict: A list of track items if `limit` is greater than 1, otherwise a single track item.

    """
    try:
        response = requests.get(query + f"&limit={limit}", headers=fetch_headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("HTTP Error:")
        raise SystemExit(e)
    except requests.exceptions.ConnectionError as e:
        print("Error Connecting:")
        raise SystemExit(e)
    except requests.exceptions.Timeout:
        print("Connection timed out:")
        raise SystemExit(e)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    data = response.json()

    if limit == 1:
        return data['tracks']['items'][0]
    return data["tracks"]["items"]

def get_total_tracks(track_data):
    """
    Retrieves the total number of tracks in the same disc as the given track.

    Parameters:
    - track_data: A dictionary representing the track information.

    Returns:
    - total_tracks: An integer representing the total number of tracks in the same disc as the given track.
    """
    album_query = track_data['album']['href']
    response = requests.get(album_query, headers=fetch_headers)
    data = response.json()

    disc_num = track_data['disc_number']

    i = 0
    current_disc = data['tracks']['items'][i]['disc_number']
    while current_disc != disc_num:
        i += 1
        current_disc = data['tracks']['items'][i]['disc_number']
    
    total_tracks = 1
    while i < len(data['tracks']['items']) - 1:
        current_disc = data['tracks']['items'][i]['disc_number']
        next_disc = data['tracks']['items'][i+1]['disc_number']
        if current_disc != next_disc:
            break
        total_tracks += 1
        i += 1
    
    return total_tracks

def get_total_discs(track_data):
    """
    Retrieves the total number of discs in the album of the given track.

    Parameters:
    track_data (dict): A dictionary representing the track information.

    Returns:
    int: The total number of discs in the album.
    """
    album_query = track_data['album']['href']
    response = requests.get(album_query, headers=fetch_headers)
    data = response.json()

    return data['tracks']['items'][-1]['disc_number']

def write_tags(audio, track_data):
    """
    Writes the track information to the audio file's tags.

    Parameters:
        audio (Audio): A mutagen FileType instance containing audio information including tags and filename.
        track (dict): The track information fetched from Spotify's API.
    """
    audio.tags['title'] = track_data['name']

    artists = []
    for artist in track_data['artists']:
        artists.append(artist['name'])
    audio.tags['artist'] = artists

    audio.tags['album'] = track_data['album']['name']

    # !!! Todo: Add option to configure following behavior 
    # If there are multiple album artists, set it to "Various Artists" instead
    if len(track_data['album']['artists']) > 1:
            audio.tags['albumartist'] = "Various Artists"
    else:
        audio.tags['albumartist'] = track_data['album']['artists'][0]['name']

    if args.fulldate:
        audio.tags['date'] = track_data['album']['release_date']
    else:
        audio.tags['date'] = track_data['album']['release_date'][:4]

    # -------------- Track and Disc Numbering -------------- #
    total_tracks = get_total_tracks(track_data)
    total_discs = get_total_discs(track_data)
    if isinstance(audio, EasyID3) or isinstance(audio, EasyMP3):
        audio.tags['tracknumber'] = str(track_data['track_number']) + '/' + str(total_tracks)
        if (args.keep_one_disc and total_discs == 1) or total_discs > 1:
            audio.tags['discnumber'] = str(track_data['disc_number']) + '/' + str(total_discs)
        elif 'discnumber' in audio.tags:
            del(audio.tags['discnumber'])
    else:
        audio.tags['tracknumber'] = str(track_data['track_number'])
        audio.tags['tracktotal'] = str(total_tracks)
        if (args.keep_one_disc and total_discs == 1) or total_discs > 1:
            audio.tags['discnumber'] = str(track_data['disc_number'])
            audio.tags['disctotal'] = str(total_discs)
        else:
            if 'discnumber' in audio.tags:
                del(audio.tags['discnumber'])
            if 'disctotal' in audio.tags:
                del(audio.tags['disctotal'])

    audio.save()

def embed_cover_art(audio, track_data):
    """
    Embeds cover art into an audio file.

    Parameters:
        audio (mutagen.File): The audio file object to embed the cover art into.
        track_data (dict): A dictionary containing track metadata, including the album image URL.
    """
    picture_content = requests.get(track_data['album']['images'][0]['url']).content

    if isinstance(audio, EasyID3) or isinstance(audio, EasyMP3):
        audio = ID3(audio.filename)
    if isinstance(audio, ID3):
        apic = mutagen.id3.APIC(
                encoding=3, # 3 is for utf-8
                mime='image/jpeg', # image/jpeg or image/png
                type=3, # 3 is for the cover image
                desc='Cover',
                data=picture_content
            )
        audio.delall('APIC')
        audio.add(apic)
        audio.save()
    elif isinstance(audio, FLAC) or isinstance(audio, OggVorbis):
        picture = mutagen.flac.Picture()
        picture.type = 3
        picture.mime = 'image/jpeg'
        picture.desc = 'Cover'
        picture.data = picture_content
        
        if isinstance(audio, FLAC):
            audio.clear_pictures()
            audio.add_picture(picture)
        else:
            encoded_data = b64encode(picture.write())
            vcomment_value = encoded_data.decode("ascii")
            audio['metadata_block_picture'] = [vcomment_value]
        audio.save()
        
def format_track_data(track_data):
        return f"Track: {track_data['artists'][0]['name']} - {track_data['name']}\n   Album: {track_data['album']['name']}"

# ------------------ Argument Parsing ------------------ #
parser = argparse.ArgumentParser(
    prog="gust",
    description="Get Ur Songs Tagged with metadata from Spotify")

parser.add_argument('-p', '--path', type=str, required=False, default=os.path.curdir, help="The path to the music files, defaults to the current directory")
parser.add_argument('-i', '--interactive', action='store_true', help="select tags from query results interactively")
parser.add_argument('-f', '--fulldate', action='store_true', help="use full date instead of just the year")
parser.add_argument('-d', '--keep-one-disc', action='store_true', help="keep disc tags even if there's only one disc")
parser.add_argument('--config-api', action='store_true', help="configure Spotify API credentials")
parser.add_argument('--config-reset', action='store_true', help="reset config.json (mainly for debug purpose)")
parser.add_argument('--refresh-token', action='store_true', help="refresh access token")
# parser.add_argument('--config', type=str, required=False, help="The path to the config file.")

args = parser.parse_args()
path = args.path

# -------------------- Load config -------------------- #
app_config_path = os.path.expandvars("%APPDATA%/gust/") if os.name == 'nt' else os.path.expanduser("~/.config/gust/")
app_config_file_path = os.path.join(app_config_path, 'config.json')

if args.config_reset:
    config_reset()
    print("Config reset.")
    exit()

app_config = config_load()

if args.refresh_token:
    refresh_access_token()
    print("Access token refreshed.")
    exit()
    
while True:
    if not os.path.exists(path):
        print("\nThe specified path does not exist.")
        path = questionary.path("Retry with another path:", only_directories=True).ask()
    else:
        break

# ------------------- Global variables ------------------- #
access_token = get_access_token()
fetch_headers = {'Authorization': f'Bearer {access_token}'}

def main():
    # Clear the console
    _=os.system('cls' if os.name == 'nt' else 'clear')

    print("Reading audio files...")
    audio_items = read_audio_files()

    questionary_style = Style([
        ('qmark', 'fg:#fcba3f bold'),       # token in front of the question
        ('question', 'bold'),               # question text
        ('answer', 'fg:#fcba3f bold'),      # submitted answer text behind the question
        ('pointer', 'fg:#fcba3f bold'),     # pointer used in select and checkbox prompts
        ('highlighted', 'fg:#fcba3f bold'), # pointed-at choice in select and checkbox prompts
        ('selected', 'fg:#fcba3f'),         # style for a selected item of a checkbox
        ('separator', 'fg:#f4ce86'),        # separator in lists
        ('instruction', ''),                # user instructions for select, rawselect, checkbox
        ('text', ''),                       # plain text
        ('disabled', 'fg:#858585 italic')   # disabled choices for select and checkbox prompts
    ])


    # # Configuration options
    # config = questionary.form(
    #     interactive = questionary.confirm("Interactive selection of tags?", default=False, style=questionary_style),
    #     year_only = questionary.confirm("Use only the year for the date tag?", style=questionary_style),
    #     remove_one_disc = questionary.confirm("Remove disc number if there's only one disc?", style=questionary_style)
    # ).ask()

    if not(args.interactive):
        print("Applying tags automatically...")

        for audio in audio_items:

            print(f"Processing: {audio.filename}")

            track_data = fetch_tracks(build_query(audio), 1)
            
            write_tags(audio, track_data)
            embed_cover_art(audio, track_data)
        
    else:
        print("Applying tags interactively...")

        for audio in audio_items:

            print()
            print("Current File: " + "\033[1m" + str(audio.filename) + "\033[0m")

            tracks_data = fetch_tracks(build_query(audio), 5)

            # A list of track choices for the user to select from
            track_choices = []
            for i, track_data in enumerate(tracks_data):
                track_choices.append(questionary.Choice(format_track_data(track_data), i))

            selected_track = questionary.select("Which track data do you want?", choices=track_choices, style=questionary_style).ask()

            print("Writing tags...")
            write_tags(audio, tracks_data[selected_track])
            embed_cover_art(audio, tracks_data[selected_track])

    print("\nDone.")
    questionary.press_any_key_to_continue().ask()

if __name__ == "__main__":
    main()