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

__all__ = ('VERSION',)

# XXX: IT IS VERY IMPOTANT THAT NOTHING HAPPENS BEFORE APP IS DECLARED

from flask import Flask

app = Flask(__name__)

# Build configuration
app.config.from_object('playa.conf.PlayaConfig')
app.config.from_envvar('PLAYA_SETTINGS', silent=True)

def run(func):
    """
    We wrap all initialization logic (post-config)
    inside of the run method to ensure that any
    changes to configuration (at run-time) are loaded
    before background tasks fire.
    """
    def wrapped(*args, **kwargs):
        # Init ZODB
        from playa.db import db
        db.init_app(app)

        # Init audio player
        from playa.ext.audio import AudioPlayer

        app.player = AudioPlayer(app)
    
        return func(*args, **kwargs)
    return wrapped

app.run = run(app.run)

# Import views/templatetags to ensure registration
import playa.web.context_processors
import playa.web.templatetags
import playa.web.api
import playa.web.frontend
