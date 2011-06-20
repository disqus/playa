"""
playa.web.templatetags
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import urllib

from playa import app

@app.template_filter('duration')
def duration(seconds):
    return '%s:%s' % (int(seconds / 60), ('0' + str(int(seconds % 60)))[-2:])

@app.template_filter('song_title')
def song_title(full_path):
    try:
        metadata = app.player.get_metadata(full_path)
    except KeyError:
        return full_path

    if 'artist' in metadata and 'title' in metadata:
        return '%s - %s' % (metadata['artist'], metadata['title'])

    elif 'title' in metadata:
        return metadata['title']

    return full_path

app.template_filter('urlquote')(urllib.quote)