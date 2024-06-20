import mutagen
import requests
import os
import setuptools
from base64 import b64encode
from dotenv import load_dotenv

# Environment Variables
load_dotenv()
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# Spotify Authoization using Client Credentials
auth_url = "https://accounts.spotify.com/api/token"
auth_headers = {'Authorization': f'Basic {b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode()).decode('utf-8')}'}
auth_data = {'grant_type': 'client_credentials'}

# Getting the access token for Spotify's API
auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
access_token = auth_response.json().get('access_token')
# Set headers
fetch_headers = {'Authorization': f'Bearer {access_token}'}

path = './' # path to the music files
all_items = os.listdir(path)
music_items = [item for item in all_items if os.path.isfile(os.path.join(path, item)) and mutagen.File(item) != None]

def search_tracks(limit=5):
    if "title" in audio.tags and "artist" in audio.tags:
        query = f"https://api.spotify.com/v1/search?q={audio.tags["title"]}+-+{audio.tags["artist"]}&type=track&limit={limit}" 
        # add album to query if it's available
        if "album" in audio.tags:
            query = f"https://api.spotify.com/v1/search?q={audio.tags["title"]}+-+{audio.tags["artist"]}+-+{audio.tags["album"]}&type=track&limit={limit}" 
    else:
        # use filename to search as a last resort
        query = f"https://api.spotify.com/v1/search?q={audio.filename}&type=track&limit={limit}"

    fetch_response = requests.get(query, headers=fetch_headers)
    result = fetch_response.json()
    return result["tracks"]["items"]

def display_results(results):
    for i, result in enumerate(results):
        title = result['name']
        artists = []
        for artist in result['artists']:
            artists.append(artist['name'])
        
        album = result['album']['name']
        print(f"{i+1}. {title} by {', '.join(artists)} in album {album}")

    

for item in music_items:
    audio = mutagen.File(item, easy=True)
    print(f"Processing: {audio.filename}")

    tracks = search_tracks()

    print("Results:")
    # for track in tracks:

    display_results(tracks)
    print()

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