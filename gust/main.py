import os
from sys import exit

import questionary

from cli import parse_args
from config import config_reset, config_read, config_api
from api_spotify import fetch_tracks, refresh_access_token
from tagging import embed_cover_art, read_audio_files, write_tags
from utils import build_query, format_track_display


questionary_style = questionary.Style([
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

def main():
    args = parse_args()

    if args.command == "config":
        if args.config_action == "reset":
            config_reset()
            print("Config reset.")
        elif args.config_action == "api":
            config_api()
        exit()

    config = config_read()
    if not config['api']['spotify_client_id'] or not config['api']['spotify_client_secret']:
        config_api()
        config = config_read()

    refresh_access_token(config)
    
    if not os.path.exists(args.path):
        print("The specified path does not exist.")
        exit()

    # Clear the console
    _=os.system('cls' if os.name == 'nt' else 'clear')

    print("Reading audio files...")
    audio_items = read_audio_files(args.path)

    if len(audio_items) == 0:
        exit()

    if not(args.interactive):
        print("Applying tags automatically...")

        for audio in audio_items:

            print(f"Processing: {audio.filename}")

            track_data = fetch_tracks(build_query(audio), 1)[0]
            
            write_tags(audio, track_data, args)
            embed_cover_art(audio, track_data['album']['images'][0]['url'])

    else:
        print("Applying tags interactively...")

        for audio in audio_items:

            print()
            print("Current File: " + "\033[1m" + str(audio.filename) + "\033[0m")

            tracks = fetch_tracks(build_query(audio), 5)

            # A list of track choices for the user to select from
            track_choices = []
            for i, track_data in enumerate(tracks):
                track_choices.append(questionary.Choice(format_track_display(track_data), i))

            selected = questionary.select("Which track data do you want?", choices=track_choices, style=questionary_style).ask()

            print("Writing tags...")
            write_tags(audio, tracks[selected], args)
            embed_cover_art(audio, tracks[selected]['album']['images'][0]['url'])

    print("\nDone.")

if __name__ == "__main__":
    main()