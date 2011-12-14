"""
playa
~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('playa').version
except Exception, e:
    VERSION = 'unknown'

__all__ = ('VERSION', 'app')


from flask import Flask

app = Flask(__name__)

# Build configuration
app.config.from_object('playa.conf.PlayaConfig')

# Init ZODB
from playa.db import db
db.init_app(app)


@app.before_request
def init_audio():
    if hasattr(app, 'player'):
        return
    # Init audio player
    from playa.ext.audio import AudioPlayer

    app.player = AudioPlayer(app)


@app.before_request
def init_disqus():
    if hasattr(app, 'disqus'):
        return
    import disqusapi

    app.disqus = disqusapi.DisqusAPI(app.config['DISQUS_SECRET'], app.config['DISQUS_PUBLIC'])


# Import views/templatetags to ensure registration
import playa.web.context_processors
import playa.web.templatetags
import playa.web.api
import playa.web.frontend

if __name__ == '__main__':
    app.run()