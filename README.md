Spotify and Spotify Connect CLI
===============================

version number: 0.1
author: Hicham Tahiri

Overview
--------

Python package to control Spotify and Spotify Connect without requiring spotify official client locally installed.

Uses the awesome [Spotipy](https://github.com/plamere/spotipy) library.


Installation
--------------------

To install use pip:

    $ pip install spoticonnect


Or clone the repo:

    $ git clone https://github.com/aerospeace/spoticonnect.git
	$ cd spoticonnect
    $ python setup.py install

Initial setup
--------------------

To get started, install spoticonnect and create an app on https://developers.spotify.com/

Run `spoticonnect` a first time to run the initial environment setup.
1. The environment setup will ask you to input your app details (i.e. username, client_id, client_secret and redirect_url).
    * The redirect url can be any valid url not bound, for instance http://localhost:888/callback
    * Those credentials will be saved in ~/.config/spoticonnect/configuration.ini
2. The underlying awesome library [Spotipy](https://github.com/plamere/spotipy) will then take charge of opening a browser window for you to authorise spoticonnect to access your Spotify app api.
3. Following approval, you will have to copy the final url back to your terminal (Yes this is a convoluted process, please blame Spotify, and not nor [Spotipy](https://github.com/plamere/spotipy) developpers.

Usage
--------------------
```
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
```


Contributing
------------

TBD