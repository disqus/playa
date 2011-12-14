"""
playa.web.helpers
~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from __future__ import division

from playa import app


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
        'title': metadata['title'],
        'artist': metadata.get('artist'),
        'album': metadata.get('album'),
        'position': position[0],
        'duration': position[1],
        'percent_complete': percent_complete
    }
