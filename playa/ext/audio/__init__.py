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
            self.thread = None

    def init_app(self, app):
        self.app = app
        self.index = AudioIndex(app=app, filter_keys=self.filter_keys, text_keys=self.text_keys)
        self.index.start()
        self.thread = AudioStream(app, self.index)
        self.thread.start()

    def __getattr__(self, attr):
        if attr in self.__dict__:
            if not self.thread.is_ready():
                return

            return self.__dict__[attr]
        else:
            return getattr(self.thread, attr)

    def shuffle_all(self):
        self.thread.queue = self.index.files
        random.shuffle(self.thread.queue)

    def get_num_songs(self):
        return len(self.index.files)

    def get_num_playlist_songs(self):
        return len(self.thread.queue)

    def get_song_pos(self):
        return (self.thread.pos_cur, self.thread.pos_end)

    def get_current_song(self):
        if not self.is_ready():
            return

        return self.thread.current_song

    def play_random(self):
        if not self.is_ready():
            return
        
        name = self.index.files[random.randint(0, len(self.index.files))]

        return self.play_filename(name)

    def stop_playing(self):
        self.thread.stop_audio()

    def start_playing(self):
        if not self.thread.queue and not self.thread.current_song:
            self.thread.queue = list(self.index.files)
            random.shuffle(self.thread.queue)

        self.thread.start_audio()

    def clear_playlist(self):
        self.thread.queue = []

    def get_playlist_index(self):
        return self.thread.queue_pos

    def has_playlist(self):
        return bool(self.thread.queue)

    def get_playlist_offset(self):
        current_offset = self.get_playlist_index()
        return current_offset - 2 if current_offset > 3 else 0

    def list_playlist(self, with_playing=False, limit=None):
        current_offset = self.get_playlist_index()
        if not limit:
            start = 0
            end = None
        else:
            start = self.get_playlist_offset()
            end = start + limit
            
        for num, song in enumerate(self.thread.queue[start:end]):
            if with_playing:
                yield start + num + 1, song, start + num == current_offset
            else:
                yield start + num + 1, song

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

        self.thread.queue.append(filename)
        self.thread.stopped = False
        self.thread.skipped = False

    def list_by_metadata(self, key, value=None, limit=None):
        data = self.index.filters[key]
        if value:
            data = data[value]

        for item in data:
            yield item

    def play(self):
        if not self.is_ready():
            return

        self.thread.stopped = False
        self.thread.skipped = False
    
    def pause(self):
        if not self.is_ready():
            return

        self.thread.stopped = True
        self.thread.skipped = False