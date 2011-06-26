"""
playa.models
~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from BTrees.OOBTree import OOBTree
from playa.ext.zodb import Model, Timestamp, Boolean, \
                           UUID4, List

import bcrypt
import uuid

class Users(OOBTree):
    def new(self, username, password):
        user = User(username=username)
        user.set_password(password)
        self[username] = user
        return user

class User(Model):
    username = None
    password = None
    date_created = Timestamp
    
    def __unicode__(self):
        return self.username

    def check_password(self, password):
        salt, hash = self.password.split('$', 1)

        return bcrypt.hashpw(password, salt) == hash

    def set_password(self, password):
        salt = bcrypt.gensalt()

        self.password = bcrypt.hashpw(password, salt)

class Playlists(OOBTree):
    def new(self, name, owner=None):
        id = uuid.uuid4().hex
        playlist = Playlist(id=id, name=name, owner=owner)
        self[id] = playlist
        return playlist

class Playlist(Model):
    id = UUID4
    name = None
    owner = User
    collaborative = Boolean
    date_created = Timestamp
    files = List
    
    def __unicode__(self):
        return self.name
