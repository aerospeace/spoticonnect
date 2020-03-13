#!/usr/bin/env python3
import datetime
import os
import sys
import spotipy
import click
import click_config_file
from appdirs import AppDirs
from spoticonnect import __name__ as app_name
from configobj import ConfigObj

# Set up default cache location to be used as default to the click group
app_dirs = AppDirs(app_name)
user_cache_dir = app_dirs.user_cache_dir
default_cache_file = f"{user_cache_dir}/cache"
# scope as defined per spotify to have access to all the required functionalities
scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'


@click.group(invoke_without_command=True)
@click.option('--cache-file', default=default_cache_file, type=click.Path(file_okay=True, dir_okay=False))
@click.option('--username', envvar='SPOTIPY_USERNAME', required=True,
              help='Environment variable: SPOTIPY_USERNAME', default="")
@click.option('--client-id', envvar='SPOTIPY_CLIENT_ID', required=True,
              help='Environment variable: SPOTIPY_CLIENT_ID', default="")
@click.option('--client-secret', envvar='SPOTIPY_CLIENT_SECRET', required=True,
              help='Environment variable: SPOTIPY_CLIENT_SECRET', default="")
@click.option('--redirect-uri', envvar='SPOTIPY_REDIRECT_URI', required=True,
              help='Environment variable: SPOTIPY_REDIRECT_URI', default="")
@click_config_file.configuration_option()
@click.pass_context
def cli(ctx, cache_file, username, client_id, client_secret, redirect_uri):
    ctx.ensure_object(dict)
    ctx.obj['username'] = username
    ctx.obj['client_id'] = client_id
    ctx.obj['client_secret'] = client_secret
    ctx.obj['redirect_uri'] = redirect_uri
    if ctx.invoked_subcommand == 'get-token':
        # To Improve: we are passing the default config file to write in, even if another was provided in command line
        config_file = os.path.join(click.get_app_dir(ctx.info_name), 'config')
        ctx.obj['cache_file'] = cache_file
        ctx.obj['config_file'] = config_file
        return
    if (not cache_file) or (not username) or (not client_id) or (not client_secret) or (not redirect_uri):
        click.echo('Please re-run with subcommand \"get-token\" to setup the required credentials')
        sys.exit(2)
    # else everything setup, either through environment variable, config variable or directly in command line
    token = spotipy.util.prompt_for_user_token(scope=scope,
                                               username=username,
                                               client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               cache_path=cache_file)
    sp = spotipy.Spotify(auth=token)
    ctx.obj['sp'] = sp


@cli.command()
@click.pass_context
def get_token(ctx):
    cache_file = ctx.obj['cache_file']
    config_file = ctx.obj['config_file']
    username = ctx.obj['username'] or click.prompt('Please enter spotify username')
    client_id = ctx.obj['client_id'] or click.prompt('Please enter spotify client_id')
    client_secret = ctx.obj['client_secret'] or click.prompt('Please enter spotify client_secret')
    redirect_uri = ctx.obj['redirect_uri'] or click.prompt('Please enter spotify redirect_uri')
    spotipy.util.prompt_for_user_token(scope=scope,
                                       username=username,
                                       client_id=client_id,
                                       client_secret=client_secret,
                                       redirect_uri=redirect_uri,
                                       cache_path=cache_file)
    # Note that for now the config is automatically saved in the default location!
    config = ConfigObj(unrepr=True)
    config.filename = config_file
    config['cache_file'] = cache_file
    config['username'] = username
    config['client_id'] = client_id
    config['client_secret'] = client_secret
    config['redirect_uri'] = redirect_uri
    config.write()


@cli.command()
@click.option('--query-type',
              type=click.Choice(['artist', 'album', 'playlist', 'track'], case_sensitive=False),
              required=True)
@click.argument('query')
@click.pass_context
def play(ctx, query_type, query):
    sp = ctx.obj['sp']
    search_result = sp.search(q=query, limit=1, type=query_type)
    items = search_result[f"{query_type}s"]['items']
    if not items:
        click.echo("No matching results", err=True)
        return
    context_uri = items[0]["uri"]
    if query_type == 'track':
        sp.start_playback(uris=[context_uri])
    else:
        sp.start_playback(context_uri=context_uri)


@cli.command()
@click.pass_context
def next(ctx):
    sp = ctx.obj['sp']
    sp.next_track()


@cli.command()
@click.pass_context
def previous(ctx):
    sp = ctx.obj['sp']
    sp.previous_track()


@cli.command()
@click.pass_context
def replay(ctx):
    sp = ctx.obj['sp']
    sp.seek_track(position_ms=0)


@cli.command()
@click.pass_context
def pause_or_play(ctx):  # note the command becomes pause-or-play
    sp = ctx.obj['sp']
    currently_playing = sp.currently_playing()
    if currently_playing['is_playing']:
        sp.pause_playback()
    else:
        sp.start_playback()


@cli.command()
@click.option('--relative/--absolute', default=True)
@click.argument('level', default=5)
@click.pass_context
def volume(ctx, relative, level):
    sp = ctx.obj['sp']
    volume_level = level
    if relative:
        current_playback = sp.current_playback()
        volume_level = int(current_playback['device']['volume_percent']) + level
    volume_level = max(0, min(100, volume_level))
    sp.volume(volume_level)


@cli.command()
@click.pass_context
def toggle_shuffle(ctx):  # note the command becomes toggle-shuffle
    sp = ctx.obj['sp']
    current_playback = sp.current_playback()
    old_shuffle_state = current_playback['shuffle_state']
    new_shuffle_state = not old_shuffle_state
    sp.shuffle(new_shuffle_state)


@cli.command()
@click.pass_context
def toggle_repeat(ctx):  # note the command becomes toggle-shuffle
    sp = ctx.obj['sp']
    current_playback = sp.current_playback()
    old_repeat_state = current_playback['repeat_state']
    if old_repeat_state == 'track':
        new_repeat_state = 'context'
    elif old_repeat_state == 'context':
        new_repeat_state = 'off'
    else:
        new_repeat_state = 'track'
    sp.repeat(new_repeat_state)


@cli.command()
@click.argument('formatting', default="{track}")
@click.pass_context
def status(ctx, formatting):
    sp = ctx.obj['sp']
    currently_playing = sp.currently_playing()
    if currently_playing is None:
        click.echo("NA")
        return
    format_dict = {'status': 'playing' if currently_playing['is_playing'] else 'stopped',
                   'artist': currently_playing['item']['artists'][0]['name'],
                   'album': currently_playing['item']['album']['name'], 'track': currently_playing['item']['name'],
                   'progress': datetime.timedelta(milliseconds=currently_playing['progress_ms']),
                   'length': datetime.timedelta(milliseconds=currently_playing['item']['duration_ms']),
                   'volume': ""}
    if currently_playing['is_playing']:
        current_playback = sp.current_playback()
        format_dict['volume'] = current_playback['device']['volume_percent']
    click.echo(formatting.format(**format_dict))


# To improve so that the default can be used by other people, probably through configuration file
@cli.command()
@click.argument('device_name', default="Echo Bedroom")
@click.pass_context
def transfer(ctx, device_name):
    sp = ctx.obj['sp']
    devices = sp.devices()['devices']
    # Cannot use next as been overriden with pause and play control
    computer = (device for device in devices if device['type'] == 'Computer').__next__()
    speaker = (device for device in devices if device['name'] == device_name).__next__()
    device_id = speaker['id'] if computer['is_active'] else computer['id']
    sp.transfer_playback(device_id)


@cli.command()
@click.pass_context
def is_playing(ctx):
    sp = ctx.obj['sp']
    currently_playing = sp.currently_playing()
    if not currently_playing['is_playing']:
        sys.exit(1)


def main():
    from click.testing import CliRunner
    runner = CliRunner()
    runner.invoke(cli, ['volume', '--', '-5'])


if __name__ == "__main__":
    cli()
