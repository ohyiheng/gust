from base64 import b64encode
import time
import requests

from config import config_read, config_write


def fetch_tracks(query, limit=10):
    """
    Fetches tracks from Spotify API based on the given query.

    Parameters:
        query (str): The search query for tracks.
        limit (int, optional): The maximum number of tracks to fetch. Defaults to 5.

    Returns:
        list: A list of track items.

    """
    try:
        response = requests.get(query + f"&limit={limit}", headers=get_headers())
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

    return data["tracks"]["items"]

def get_total_tracks_in_disc(track_data):
    """
    Retrieves the total number of tracks in the same disc as the given track.

    Parameters:
    - track_data: A dictionary representing the track information.

    Returns:
    - total_tracks: An integer representing the total number of tracks in the same disc as the given track.
    """
    album_query = track_data['album']['href']
    response = requests.get(album_query, headers=get_headers())
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

def get_total_discs(track_data) -> int:
    """
    Retrieves the total number of discs in the album of the given track.

    Parameters:
        track_data (dict): A dictionary representing the track information.

    Returns:
        int: The total number of discs in the album.
    """
    album_query = track_data['album']['href']
    response = requests.get(album_query, headers=get_headers())
    data = response.json()

    return data['tracks']['items'][-1]['disc_number']

def get_headers():
    return {'Authorization': f'Bearer {get_access_token()}'} 

def get_access_token():
    """
    Retrieves the access token for Spotify's API using the client credentials flow.

    Returns:
        str: The access token for Spotify's API.
    """
    config = config_read()

    if (not config['api']['spotify_access_token']['expires'] or
        float(config['api']['spotify_access_token']['expires']) < time.time()):
        return refresh_access_token(config)
    else:    
        return config['api']['spotify_access_token']['token']

def refresh_access_token(config, retry_count=0):
    if retry_count > 2:
        print("Failed to get access token. Please try again later.")
        raise SystemExit()
    
    spotify_c_id = config['api']['spotify_client_id']
    spotify_c_secret = config['api']['spotify_client_secret']

    auth_url = "https://accounts.spotify.com/api/token"
    auth_headers = {
        'Authorization': f"Basic {b64encode(f'{spotify_c_id}:{spotify_c_secret}'.encode()).decode('utf-8')}"
    }
    auth_data = {'grant_type': 'client_credentials'}

    try:
        auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
        auth_response.raise_for_status()
        access_token = auth_response.json().get('access_token')
    except requests.exceptions.HTTPError as e:
        print("HTTP Error: Maybe your Spotify Client ID or Secret is incorrect? Run `gust config api` to reconfigure.")
        raise SystemExit(e)
    except requests.exceptions.ConnectionError as e:
        print("Error Connecting:")
        raise SystemExit(e)
    except requests.exceptions.Timeout:
        print("Connection timed out. Retrying in 5 seconds...")
        time.sleep(5)
        access_token = refresh_access_token(retry_count + 1)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    config['api']['spotify_access_token']['token'] = access_token
    config['api']['spotify_access_token']['expires'] = time.time() + 3600
    config_write(config)
    
    return access_token