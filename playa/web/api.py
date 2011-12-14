"""
playa.web.api
~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from playa import app
from playa.web.helpers import get_now_playing

from flask import request, redirect, url_for

import functools
import simplejson


def api(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        resp = func(*args, **kwargs)
        if not request.is_xhr:
            return redirect(url_for('index'))
        return simplejson.dumps(resp or {})
    return wrapped


@app.route('/api/now_playing', methods=['GET'])
@api
def now_playing():
    return get_now_playing()


@app.route('/api/set_volume', methods=['POST'])
@api
def set_volume():
    value = request.form['value']
    app.player.set_volume(value)

    return {
        'value': app.player.get_volume()
    }


@app.route('/api/seek', methods=['POST'])
@api
def seek():
    pos = request.form['pos']
    app.player.seek(pos)


@app.route('/api/queue/add', methods=['POST'])
@api
def add_to_queue():
    filename = request.form['filename']

    if not app.player.has_song(filename):
        return {'error': 'file not in index'}

    if filename in request.user.queue:
        return {'error': 'file already in queue'}

    request.user.queue.append(filename)
    return {'filename': filename}


@app.route('/api/shuffle_all', methods=['POST'])
@api
def shuffle_all():
    app.player.shuffle_all()
