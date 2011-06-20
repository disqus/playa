"""
playa.web.context_processors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from playa import app
from playa.web.helpers import get_now_playing

@app.context_processor
def player():
    return {
        'now_playing': get_now_playing(),
        'total_songs': app.player.get_num_songs(),
        'playlist_songs': app.player.get_num_playlist_songs(),
        'player': app.player,
    }
