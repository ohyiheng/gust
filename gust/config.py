import json
import os
import questionary


config_dir = os.path.expandvars("%APPDATA%/gust/") if os.name == 'nt' else os.path.expanduser("~/.config/gust/")
config_file = os.path.join(config_dir, 'config.json')

def config_reset():
    os.makedirs(config_dir, exist_ok=True)

    with open(config_file, 'w') as file:
        file.truncate()
        config = {"api": {
            "spotify_client_id": "",
            "spotify_client_secret": "",
            "spotify_access_token": {
                "token": "",
                "expires": ""
            }
        }}
        json.dump(config, file, indent=4)

def config_read():
    # Create the config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    # Initialise config if it doesn't exist
    if not os.path.exists(config_file):
        config_reset()
        
    with open(config_file, 'r') as file:
        try:
            config = json.load(file)
        except json.JSONDecodeError as e:
            print("Error decoding config.json")
            raise SystemExit(e)

    return config

def config_write(config):
    # Create the config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    # Initialise config if it doesn't exist
    if not os.path.exists(config_file):
        config_reset()

    with open(config_file, 'w') as file:
        file.truncate()
        new_config = config
        json.dump(new_config, file, indent=4)
    
def config_api():
    config = config_read()
    client_id, client_secret = _prompt_api()
    config['api']['spotify_client_id'] = client_id
    config['api']['spotify_client_secret'] = client_secret
    config_write(config)

def _prompt_api():
    client_id = questionary.text("Spotify Client ID:").ask()
    client_secret = questionary.password("Spotify Client Secret:").ask()
    return client_id, client_secret