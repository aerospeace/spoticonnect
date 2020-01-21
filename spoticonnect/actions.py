import pyperclip
from docopt import DocoptExit
from spoticonnect.utils import print_status, print_error
from spoticonnect.configuration import Configuration
import spotipy
import datetime

configuration = Configuration()
configuration.load()
sp = configuration.get_spotify()


def next_track(args):
    print_status("Playing next track")
    sp.next_track()
    status()


def previous_track(args):
    print_status("Playing previous track")
    sp.previous_track()
    status()


def replay(args):
    print_status("Playing track from the beginning")
    sp.seek_track(position_ms=0)
    status()


def pause(args):
    print_status("Pausing Spotify")
    _pause()
    status()


def stop(args):
    print_status("Stopping Spotify")
    _pause()
    sp.seek_track(position_ms=0)
    status()


def vol(args):
    vol_step = 5
    volume = _get_volume_percent()
    if args["show"]:
        print_status(f"Volume: {volume}")
    elif args["up"]:
        new_vol = min(int(volume) + vol_step, 100)
        sp.volume(new_vol)
        print_status(f"Volume: {new_vol}")
    elif args["down"]:
        new_vol = max(int(volume) - vol_step, 0)
        sp.volume(new_vol)
        print_status(f"Volume: {new_vol}")
    elif args["set"]:
        try:
            volume = int(args["<amount>"])
        except ValueError:
            print_error("Volume value must be a number between 0 and 100")
            raise DocoptExit
        sp.volume(volume)
        print_status(f'Volume: {args["<amount>"]}')


def toggle_shuffle(args):
    old_shuffle_state = _get_shuffle_state()
    new_shuffle_state = not old_shuffle_state
    sp.shuffle(new_shuffle_state)
    print_status(f"Shuffle mode {'on' if new_shuffle_state else 'off'}")


def toggle_repeat(args):
    old_repeat_state = _get_repeat_state()
    print(old_repeat_state)
    if old_repeat_state == 'track':
        new_repeat_state = 'context'
    elif old_repeat_state == 'context':
        new_repeat_state = 'off'
    else:
        new_repeat_state = 'track'
    sp.repeat(new_repeat_state)
    print_status(f"Repeat mode {new_repeat_state}")


def status(args=None):
    playing_status, artist_name, album_name, track_name, curr_pos, total_time = _get_status()
    print_status(f"Spotify is currently {playing_status}")
    print(
        f"Artist: {artist_name}\n"
        f"Album: {album_name}\n"
        f"Track: {track_name}\n"
        f"Position: {curr_pos} / {total_time}\n"
    )


def play(args):
    """
    Play current song if no additional parameters are given.
    Search and play otherwise.
    """
    if args["<query>"]:
        q = args["<query>"]
        if args['uri']:
            try:
                sp.start_playback(context_uri=q)
                print_status(f"Playing uri: {args['uri']}")
            except spotipy.client.SpotifyException:
                print_error("Invalid URI")
                return
        for query_type in ('album', 'artist', 'playlist', 'track'):
            if args[query_type]:
                type_with_s = query_type + "s"
                search_result = sp.search(q=q, limit=1, type=query_type)
                items = search_result[type_with_s]['items']
                if not items:
                    print_error("No result for this research")
                    return
                context_uri = items[0]["uri"]
                item_name = items[0]["name"]
                if query_type == 'track':
                    sp.start_playback(uris=[context_uri])
                else:
                    sp.start_playback(context_uri=context_uri)
                print_status(f"Playing {query_type}: {item_name}")
                return
    else:
        sp.start_playback()
        status()


def share(args):
    currently_playing = sp.currently_playing()
    for link_type in ('uri', 'href'):
        if args[link_type]:
            result = currently_playing['item'][link_type]
            if link_type == 'href':
                result = "https://open.spotify.com/track/" + result.split('/')[-1]
            pyperclip.copy(result)
            print_status(f"Song {link_type}: {result} copied to clipboard")
            return


# Helper functions #
def _get_volume_percent():
    current_playback = sp.current_playback()
    return current_playback['device']['volume_percent']


def _get_shuffle_state():
    current_playback = sp.current_playback()
    return current_playback['shuffle_state']


def _get_repeat_state():
    current_playback = sp.current_playback()
    return current_playback['repeat_state']


def _get_status(market='US'):
    currently_playing = sp.currently_playing(market=market)
    playing_status = 'playing' if currently_playing['is_playing'] else 'stopped'
    artist_name = currently_playing['item']['artists'][0]['name']  # can be imporved later for several artists
    album_name = currently_playing['item']['album']['name']
    track_name = currently_playing['item']['name']
    curr_pos = datetime.timedelta(milliseconds=currently_playing['progress_ms'])
    total_time = datetime.timedelta(milliseconds=currently_playing['item']['duration_ms'])
    return playing_status, artist_name, album_name, track_name, curr_pos, total_time


def _pause():
    try:
        sp.pause_playback()
    except spotipy.client.SpotifyException:
        print_error("Error in trying to pause/stop. Is a track being played?")
        return
