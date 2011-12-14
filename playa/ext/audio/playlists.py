"""
playa.ext.audio.playlists
~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from __future__ import absolute_import

import os.path

from playa.common.storage import load


class UserQueue(object):
    KEY = 'queue'

    def __init__(self, session):
        self.session = session

    def add(self, item):
        self.session.setdefault(self.KEY, []).append(item)
        self.session.modified = True

    def pop(self, item):
        self.session[self.KEY].pop()
        self.session.modified = True

    def remove(self, index):
        self.session[self.KEY].pop(index)
        self.session.modified = True

    def __iter__(self):
        return iter(self.session.get(self.KEY, []))


class Playlists(object):
    def __init__(self, app):
        self.app = app
        self.playlists = {}
        self.add_path(os.path.join(self.app.config['DATA_PATH'], 'playlists'))

    def add_path(self, path, base=None):
        if not base:
            base = path
        for fn in os.listdir(path):
            if fn.startswith('.'):
                continue

            full_path = os.path.join(path, fn)
            if os.path.isdir(full_path):
                self.add_path(path, base)
                continue

            self.playlists[full_path] = load(full_path)
