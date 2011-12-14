"""
playa.web.context_processors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from playa import app, db
from playa.web.helpers import get_now_playing

from flask import session, request


@app.before_request
def append_user():
    if 'username' not in session:
        request.user = None
    else:
        request.user = db['users'][session['username']]


@app.context_processor
def player():
    return {
        'now_playing': get_now_playing(),
        'total_songs': app.player.get_num_songs(),
        'playlist_songs': app.player.get_num_playlist_songs(),
        'player': app.player,
        'user': request.user,
    }
