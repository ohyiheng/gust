from base64 import b64encode
import os

import mutagen
from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import EasyMP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis

from api_spotify import get_total_discs, get_total_tracks_in_disc
from utils import fetch_image


def read_audio_files(path):
    audio_items = []

    for dirpath, dirs, files in os.walk(path):
        for file in files:
            if (not (file.endswith(".mp3") or
                     file.endswith(".flac") or
                     file.endswith(".ogg") or
                     file.endswith(".opus"))):
                continue

            mutagen_file = mutagen.File(
                os.path.join(dirpath, file),
                easy=True,
            )
            if (isinstance(mutagen_file, FLAC) or
                isinstance(mutagen_file, OggVorbis) or
                isinstance(mutagen_file, EasyID3) or
                isinstance(mutagen_file, EasyMP3)):
                audio_items.append(mutagen_file)
                
    if len(audio_items) == 0:
        print("No compatible audio files found in current directory.")

    return audio_items

def write_tags(audio, track_data, args):
    """
    Writes the track information to the audio file's tags.

    Parameters:
        audio (Audio): A mutagen FileType instance containing audio information including tags and filename.
        track_data (dict): The track information fetched from Spotify's API.
        args (dict): CLI arguments passed by user
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

    if args.date_full:
        audio.tags['date'] = track_data['album']['release_date']
    else:
        audio.tags['date'] = track_data['album']['release_date'][:4]

    # -------------- Track and Disc Numbering -------------- #
    total_tracks = get_total_tracks_in_disc(track_data)
    total_discs = get_total_discs(track_data)
    keep_discs = (args.always_keep_discs and total_discs == 1) or total_discs > 1

    if isinstance(audio, EasyID3) or isinstance(audio, EasyMP3):
        audio.tags['tracknumber'] = str(track_data['track_number']) + '/' + str(total_tracks)
        if keep_discs:
            audio.tags['discnumber'] = str(track_data['disc_number']) + '/' + str(total_discs)
        elif 'discnumber' in audio.tags:
            del(audio.tags['discnumber'])
    else:
        audio.tags['tracknumber'] = str(track_data['track_number'])
        audio.tags['tracktotal'] = str(total_tracks)
        if keep_discs:
            audio.tags['discnumber'] = str(track_data['disc_number'])
            audio.tags['disctotal'] = str(total_discs)
        else:
            if 'discnumber' in audio.tags:
                del(audio.tags['discnumber'])
            if 'disctotal' in audio.tags:
                del(audio.tags['disctotal'])

    audio.save()

def embed_cover_art(audio, url):
    """
    Embeds cover art into an audio file.

    Parameters:
        audio (mutagen.File): The audio file object to embed the cover art into.
        track_data (dict): A dictionary containing track metadata, including the album image URL.
    """
    picture_data = fetch_image(url)

    if not picture_data:
        return

    if isinstance(audio, EasyID3) or isinstance(audio, EasyMP3):
        audio = ID3(audio.filename)
    if isinstance(audio, ID3):
        apic = mutagen.id3.APIC(
                encoding=3, # 3 is for utf-8
                mime='image/jpeg', # image/jpeg or image/png
                type=3, # 3 is for the cover image
                desc='Cover',
                data=picture_data
            )
        audio.delall('APIC')
        audio.add(apic)
        audio.save()
    elif isinstance(audio, FLAC) or isinstance(audio, OggVorbis):
        picture = mutagen.flac.Picture()
        picture.type = 3
        picture.mime = 'image/jpeg'
        picture.desc = 'Cover'
        picture.data = picture_data
        
        if isinstance(audio, FLAC):
            audio.clear_pictures()
            audio.add_picture(picture)
        else:
            encoded_data = b64encode(picture_data.write())
            vcomment_value = encoded_data.decode("ascii")
            audio['metadata_block_picture'] = [vcomment_value]
        audio.save()