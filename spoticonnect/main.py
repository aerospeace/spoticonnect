"""
Usage:
    spoticonnect play [(album | artist | playlist | track | uri) <query>]
    spoticonnect next
    spoticonnect previous
    spoticonnect replay
    spoticonnect pause
    spoticonnect stop
    spoticonnect vol (show | up | down | set <amount>)
    spoticonnect status
    spoticonnect share (uri | href)
    spoticonnect shuffle
    spoticonnect repeat
"""
from docopt import docopt
from spoticonnect import actions


def main():
    """Main entry point for the spoticonnect CLI."""
    args = docopt(__doc__)
    commands_functions = {
        "play": actions.play,
        "status": actions.status,
        "next": actions.next_track,
        "previous": actions.previous_track,
        "replay": actions.replay,
        "pause": actions.pause,
        "stop": actions.stop,
        "vol": actions.vol,
        "share": actions.share,
        "shuffle": actions.toggle_shuffle,
        "repeat": actions.toggle_repeat,
        # "login": actions.login_wizard,
    }

    arg = next(arg for arg in args if arg in commands_functions.keys() and args[arg] is True)
    commands_functions[arg](args=args)


if __name__ == "__main__":
    main()
