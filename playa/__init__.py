"""
Playa
~~~~~
"""

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('playa').version
except Exception, e:
    VERSION = 'unknown'

__all__ = ('VERSION', 'capture')

# XXX: IT IS VERY IMPOTANT THAT NOTHING HAPPENS BEFORE APP IS DECLARED

from flask import Flask

app = Flask(__name__)

# OK CONTINUE WORKING

# Build configuration
app.config.from_object('playa.conf.PlayaConfig')
app.config.from_envvar('PLAYA_SETTINGS', silent=True)

# Setup database
from playa.ext.sqlite3 import SQLite3

app.db = SQLite3(app).get_db()

# Import views/templatetags to ensure registration
import playa.web.context_processors
import playa.web.templatetags
import playa.web.api
import playa.web.frontend
