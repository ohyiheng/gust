import requests


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

def format_track_display(track_data):
    return f"Track: {track_data['artists'][0]['name']} - {track_data['name']}\n   Album: {track_data['album']['name']}"

def fetch_image(url):
    image = None
    try:
        image = requests.get(url).content
    except requests.exceptions.RequestException as e:
        print(e)
    return image
