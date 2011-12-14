"""
playa.models
~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from BTrees.OOBTree import OOBTree
from playa.ext.zodb import Model, Timestamp, List

import bcrypt


class Users(OOBTree):
    def new(self, username, password=None):
        user = User(username=username)
        if password:
            user.set_password(password)
        self[username] = user
        return user


class User(Model):
    username = None
    password = None
    date_created = Timestamp
    queue = List

    def __unicode__(self):
        return self.username

    def check_password(self, password):
        salt, hash = self.password.split('$', 1)

        return bcrypt.hashpw(password, salt) == hash

    def set_password(self, password):
        salt = bcrypt.gensalt()

        self.password = bcrypt.hashpw(password, salt)
