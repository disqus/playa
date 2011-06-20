"""
playa.ext.audio
~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from __future__ import absolute_import

import os.path
import random

from playa.ext.audio.index import AudioIndex
from playa.ext.audio.stream import AudioStream

class AudioPlayer(object):
    filter_keys = ['title', 'artist', 'genre', 'album']
    text_keys = ['title', 'artist', 'album']
    
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None
            self.stream = None

    def init_app(self, app):
        self.app = app
        self.index = AudioIndex(app=app, filter_keys=self.filter_keys, text_keys=self.text_keys)
        self.index.start()
        self.stream = AudioStream(app, self.index)
        self.stream.start()

    def __getattr__(self, attr):
        if attr in self.__dict__:
            if not self.stream.is_ready():
                return

            return self.__dict__[attr]
        else:
            return getattr(self.stream, attr)

    def get_num_songs(self):
        return len(self.index.files)

    def get_num_playlist_songs(self):
        return len(self.stream.queue)

    def get_song_pos(self):
        return (self.stream.pos_cur, self.stream.pos_end)

    def get_current_song(self):
        if not self.is_ready():
            return

        return self.stream.get_current_song()

    def play_random(self):
        if not self.is_ready():
            return
        
        name = self.index.files[random.randint(0, len(self.index.files))]

        return self.play_filename(name)

    def find_song(self, query):
        if not self.is_ready():
            return

        return self.index.search(query) or []
    
    def get_metadata(self, filename):
        return self.index.metadata[filename]
    
    def play_filename(self, filename):
        if not self.is_ready():
            return

        if not os.path.exists(filename):
            raise ValueError

        self.stream.queue.add(filename)

    def list_by_metadata(self, key, value=None, limit=None):
        data = self.index.filters[key]
        if value:
            data = data[value]

        for item in data:
            yield item
