from playa.ext.zodb import ZODB
from playa.models import Users, Playlists

db = ZODB()

@db.init
def set_defaults(root):
    if 'users' not in root:
        root['users'] = Users()
    if 'playlists' not in root:
        root['playlists'] = Playlists()
