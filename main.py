import mutagen
import requests
import os
import setuptools
from base64 import b64encode
from dotenv import load_dotenv

print(setuptools.__version__)
load_dotenv()

spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

auth_url = "https://accounts.spotify.com/api/token"
auth_headers = {'Authorization': f'Basic {b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode()).decode('utf-8')}'}
auth_data = {'grant_type': 'client_credentials'}

auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
access_token = auth_response.json().get('access_token')

fetch_headers = {'Authorization': f'Bearer {access_token}'}

path = './'
all_items = os.listdir(path)
music_items = [item for item in all_items if os.path.isfile(os.path.join(path, item)) and mutagen.File(item) != None]
query = None

for item in music_items:
    audio = mutagen.File(item, easy=True)
    print(f"Processing: {audio.filename}")
    if "title" in audio.tags and "artist" in audio.tags:
        query = f"https://api.spotify.com/v1/search?q={audio.tags["title"]}+-+{audio.tags["artist"]}&type=track&limit=5" 
        # add album to query if it's available
        if "album" in audio.tags:
            query = f"https://api.spotify.com/v1/search?q={audio.tags["title"]}+-+{audio.tags["artist"]}+-+{audio.tags["album"]}&type=track&limit=5" 
    else:
        # use filename to search as a last resort
        query = f"https://api.spotify.com/v1/search?q={audio.filename}&type=track&limit=5" 

    fetch_response = requests.get(query, headers=fetch_headers)
    fetch_data = fetch_response.json()
    tracks = fetch_data["tracks"]["items"]

    print("Results:")
    for track in tracks:
        print(f"track: {track['name']}")
        print(f"artists: {track['artists'][0]['name']}")
        print(f"album: {track['album']['name']}")
        

# tag = {
#     "artist": "Something",
#     "album": "Another Thing"
# }

# audio.tags['artist'] = "Something"
# audio.tags['albumartist'] = "Another Thing"
# audio.tags['album'] = "Best Album"
# audio.save()
# print(audio.tags)