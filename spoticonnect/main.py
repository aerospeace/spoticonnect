#!/usr/bin/env python3
import datetime
import sys
import spotipy
import click


@click.group(invoke_without_command=True)
@click.option('--token', envvar='SPOTICONNECT_TOKEN')
@click.pass_context
def cli(ctx, token):
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand != 'get-token':
        if not token:
            click.echo('Please run with subcommand get-token to setup the required token')
            sys.exit(2)
        # else there is a token
        else:
            sp = spotipy.Spotify(auth=token)
            ctx.obj['sp'] = sp


@cli.command()
@click.option('--username', prompt=True)
@click.option('--client-id', prompt=True)
@click.option('--client-secret', prompt=True)
@click.option('--redirect-uri', prompt=True)
def get_token(username, client_id, client_secret, redirect_uri):
    scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
    token = spotipy.util.prompt_for_user_token(scope=scope,
                                               username=username,
                                               client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri)
    click.echo("Please add an environment variable SPOTICONNECT_TOKEN with the value of the following toke:")
    click.echo(token)
    click.echo("For instance, add in your .zshenv:")
    click.echo(f"export SPOTICONNECT_TOKEN={token}")

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
def pause_or_play(ctx):  # not the command becomes pause-or-play
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
def toggle_shuffle(ctx):  # not the command becomes toggle-shuffle
    sp = ctx.obj['sp']
    current_playback = sp.current_playback()
    old_shuffle_state = current_playback['shuffle_state']
    new_shuffle_state = not old_shuffle_state
    sp.shuffle(new_shuffle_state)


@cli.command()
@click.pass_context
def toggle_repeat(ctx):  # not the command becomes toggle-shuffle
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
    # main()
    cli()
