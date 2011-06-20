from playa import app
from playa.web.helpers import get_now_playing

from flask import request, redirect, url_for

import functools
import simplejson

def api(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        resp = func(*args, **kwargs)
        if request.is_xhr:
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

@app.route('/api/shuffle_all', methods=['POST'])
@api
def shuffle_all():
    app.player.shuffle_all()
