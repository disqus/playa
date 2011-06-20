from playa import app
from playa.web.helpers import get_now_playing

from flask import request

import simplejson

@app.route('/api/now_playing', methods=['GET'])
def now_playing():
    return simplejson.dumps(get_now_playing())

@app.route('/api/set_volume', methods=['POST'])
def set_volume():
    value = request.form['value']
    app.player.set_volume(value)
    return simplejson.dumps({
        'value': app.player.get_volume()
    })

@app.route('/api/seek', methods=['POST'])
def seek():
    pos = request.form['pos']
    app.player.seek(pos)
    return simplejson.dumps({})

@app.route('/api/shuffle_all', methods=['POST'])
def shuffle_all():
    app.player.shuffle_all()
    
    return redirect('/')