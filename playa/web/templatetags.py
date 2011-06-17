import urllib

from playa import app

@app.template_filter('duration')
def duration(seconds):
    return '%s:%s' % (int(seconds / 60), ('0' + str(int(seconds % 60)))[-2:])

@app.template_filter('song_title')
def song_title(metadata):
    if 'artist' in metadata:
        return '%s - %s' % (metadata['artist'], metadata['title'])
    return metadata['title']

app.template_filter('urlquote')(urllib.quote)