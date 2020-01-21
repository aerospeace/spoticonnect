import spotipy
import configparser
from appdirs import AppDirs
from pathlib import Path
from spoticonnect.utils import print_status
from spoticonnect import __name__ as app_name


class Configuration:
    def __init__(self):
        app_dirs = AppDirs(app_name)
        user_config_dir = app_dirs.user_config_dir
        user_cache_dir = app_dirs.user_cache_dir
        Path(user_config_dir).mkdir(parents=True, exist_ok=True)
        Path(user_cache_dir).mkdir(parents=True, exist_ok=True)
        self.config_file = f'{user_config_dir}/configuration.ini'
        self.cache_file = f"{user_cache_dir}/cache"
        self.config = configparser.ConfigParser()

    def load(self):
        if not self.config.read(self.config_file):
            self.set()

    def set(self):
        print_status('Initial environment setup')
        self.config['MAIN'] = {}
        self.config['MAIN']['username'] = input("Enter your username: ")
        self.config['MAIN']['client_id'] = input("Enter your client_id: ")
        self.config['MAIN']['client_secret'] = input("Enter your client_secret: ")
        self.config['MAIN']['redirect_uri'] = input("Enter your redirect_uri: ")
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def get_spotify(self):
        main_section = self.config['MAIN']
        scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
        token = spotipy.util.prompt_for_user_token(scope=scope,
                                                   username=main_section['username'],
                                                   client_id=main_section['client_id'],
                                                   client_secret=main_section['client_secret'],
                                                   redirect_uri=main_section['redirect_uri'],
                                                   cache_path=self.cache_file)
        return spotipy.Spotify(auth=token)
