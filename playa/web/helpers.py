from __future__ import division

from playa import app
from playa.web.templatetags import song_title

def get_now_playing():
    current_song = app.player.get_current_song()

    if not current_song:
        return {
            'playing': False,
        }

    position = app.player.get_song_pos()
    metadata = app.player.get_metadata(current_song)

    if not position[0]:
        percent_complete = 0
    else:
        percent_complete = position[0] / position[1] * 100

    return {
        'playing': app.player.is_playing(),
        'filename': current_song,
        'title': song_title(current_song),
        'album': metadata.get('album'),
        'position': position[0],
        'duration': position[1],
        'percent_complete': percent_complete
    }