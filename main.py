import mutagen
from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3, EasyMP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
import requests
import os
import questionary
from questionary import Style
from base64 import b64encode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

path = './' # path to the music files
all_items = os.listdir(path)
audio_items = [
    mutagen.File(item, easy=True) 
    for item in all_items 
    if os.path.isfile(os.path.join(path, item)) and mutagen.File(item) != None
]

fancy_style = Style([
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


def get_access_token():
    """
    Retrieves the access token for Spotify's API using the client credentials flow.

    Returns:
        str: The access token for Spotify's API.
    """
    # Spotify Client ID and Secret environment variables
    spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
    spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    # Spotify Authoization using Client Credentials
    auth_url = "https://accounts.spotify.com/api/token"
    auth_headers = {'Authorization': f"Basic {b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode()).decode('utf-8')}"}
    auth_data = {'grant_type': 'client_credentials'}

    # Getting the access token for Spotify's API
    auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
    return auth_response.json().get('access_token')

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

    Args:
        query (str): The search query for tracks.
        limit (int, optional): The maximum number of tracks to fetch. Defaults to 5.

    Returns:
        list or dict: A list of track items if `limit` is greater than 1, otherwise a single track item.

    """
    response = requests.get(query + f"&limit={limit}", headers=fetch_headers)
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

def write_tags(audio, track_data, year_only, remove_one_disc):
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

    # !!! Todo: Add config option to disable automatic Various Artists 
    # If there are multiple album artists, set it to "Various Artists" instead
    if len(track_data['album']['artists']) > 1:
            audio.tags['albumartist'] = "Various Artists"
    else:
        audio.tags['albumartist'] = track_data['album']['artists'][0]['name']

    if year_only:
        audio.tags['date'] = track_data['album']['release_date'][:4]
    else:
        audio.tags['date'] = track_data['album']['release_date']

    # -------------- Track and Disc Numbering -------------- #
    total_tracks = get_total_tracks(track_data)
    total_discs = get_total_discs(track_data)
    if isinstance(audio, EasyID3) or isinstance(audio, EasyMP3):
        audio.tags['tracknumber'] = str(track_data['track_number']) + '/' + str(total_tracks)
        if (not(remove_one_disc) and total_discs == 1) or total_discs > 1:
            audio.tags['discnumber'] = str(track_data['disc_number']) + '/' + str(total_discs)
    else:
        audio.tags['tracknumber'] = str(track_data['track_number'])
        audio.tags['tracktotal'] = str(total_tracks)
        if (not(remove_one_disc) and total_discs == 1) or total_discs > 1:
            audio.tags['discnumber'] = str(track_data['disc_number'])
            audio.tags['disctotal'] = str(total_discs)

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
        audio = ID3(os.path.join(path, audio.filename))
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

# ------------------- Global variables ------------------- #
load_dotenv() # Load environment variables from .env file
path = './' # Path to the music files
access_token = get_access_token()
fetch_headers = {'Authorization': f'Bearer {access_token}'}

def main():
    all_items = os.listdir(path)
    audio_items = [
        mutagen.File(item, easy=True) 
        for item in all_items 
        if os.path.isfile(os.path.join(path, item)) and mutagen.File(os.path.join(path, item)) != None
    ]

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

    # Clear the console
    _=os.system('cls' if os.name == 'nt' else 'clear')

    # Configuration options
    config = questionary.form(
        interactive = questionary.confirm("Interactive selection of tags?", default=False, style=questionary_style),
        year_only = questionary.confirm("Use only the year for the date tag?", style=questionary_style),
        remove_one_disc = questionary.confirm("Remove disc number if there's only one disc?", style=questionary_style)
    ).ask()

    if not(config['interactive']):
        print("Applying tags automatically...")

        for audio in audio_items:

            print(f"Processing: {audio.filename}")

            track_data = fetch_tracks(build_query(audio), 1)
            
            write_tags(audio, track_data, config['year_only'], config['remove_one_disc'])
            embed_cover_art(audio, track_data)
        
    else:
        print("Manual tag selection...")

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
            write_tags(audio, tracks_data[selected_track], config['year_only'], config['remove_one_disc'])
            embed_cover_art(audio, tracks_data[selected_track])

    print("\nDone.")

if __name__ == "__main__":
    main()