import mutagen
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
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

def write_tags(audio, track_data):
    """
    Writes the track information to the audio file's tags.

    Args:
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

    if year_only.lower() in ['y', 'yes', '']:
        audio.tags['date'] = track_data['album']['release_date'][:4]
    else:
        audio.tags['date'] = track_data['album']['release_date']

    if isinstance(audio, ID3) or isinstance(audio, MP3):
        audio.tags['tracknumber'] = str(track_data['track_number']) + '/' + str(get_total_tracks(track_data))
        audio.tags['discnumber'] = str(track_data['disc_number']) + '/' + str(get_total_discs(track_data))
    else:
        audio.tags['tracknumber'] = str(track_data['track_number'])
        audio.tags['tracktotal'] = str(get_total_tracks(track_data))
        audio.tags['discnumber'] = str(track_data['disc_number'])
        audio.tags['disctotal'] = str(get_total_discs(track_data))
    
def format_track_data(track_data):
        return f"Track: {track_data['artists'][0]['name']} - {track_data['name']}\n   Album: {track_data['album']['name']}"

# def main():
access_token = get_access_token()
fetch_headers = {'Authorization': f'Bearer {access_token}'}

# Configuration options
auto_tag = input("Apply tags automatically? (choosing the first result) [Y/n] ")
year_only = input("Use only the year for the album release date? [Y/n] ")
remove_one_disc = input("Remove disc info when there's only one disc? [Y/n] ")

if auto_tag.lower() in ['y', 'yes', '']:
    print("Applying tags automatically...")

    for audio in audio_items:

        print(f"Processing  : {audio.filename}")

        track_data = fetch_tracks(build_query(audio), 1)
        
        write_tags(audio, track_data)
        audio.save()

        # if remove_one_disc.lower() in ['y', 'yes', ''] and total_discs == 1:
            # don't write disc info if there's only one disc
    
else:
    print("Manual tag selection...")

    for audio in audio_items:

        print()
        print("Current File: " + "\033[1m" + str(audio.filename) + "\033[0m")

        tracks_data = fetch_tracks(build_query(audio), 5)

        track_choices = []
        for i, track_data in enumerate(tracks_data):
            track_choices.append(questionary.Choice(format_track_data(track_data), i))

        selected_track = questionary.select("Which track data do you want?", choices=track_choices, style=fancy_style).ask()

        print("Writing tags...")
        write_tags(audio, tracks_data[selected_track])
        audio.save()

print("\nDone.")

# if "__name__" == "__main__":
#     main()


    # title = tracks[0]['name']
    # print(f"track: {title}")

    # artists = []
    # for artist in tracks[0]['artists']:
    #     artists.append(artist['name'])
    # print(f"artists: {artists}")

    # album = tracks[0]['album']['name']
    # print(f"album: {album}")

    # if tracks[0]['album']['artists'].length > 1:
    #     albumartist = "Various Artists"
    # else:
    #     albumartist = tracks[0]['album']['artists'][0]
    # print(f"album artist: {albumartist}\n")
    
        

# tag = {
#     "artist": "Something",
#     "album": "Another Thing"
# }

# audio.tags['artist'] = "Something"
# audio.tags['albumartist'] = "Another Thing"
# audio.tags['album'] = "Best Album"
# audio.save()
# print(audio.tags)