from playa import app
from playa.web.helpers import get_now_playing

import simplejson

@app.route('/api/now_playing', methods=['GET'])
def now_playing():
    return simplejson.dumps(get_now_playing())
