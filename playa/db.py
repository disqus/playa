"""
playa.db
~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from playa.ext.zodb import ZODB
from playa.models import Users, Playlists

db = ZODB()

@db.init
def set_defaults(root):
    if 'users' not in root:
        root['users'] = Users()
    if 'playlists' not in root:
        root['playlists'] = Playlists()
