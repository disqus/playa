from __future__ import absolute_import

import mad
import os
import pyaudio
import random
import re
import threading
import time
import wave
from collections import defaultdict
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

class AudioIndex(threading.Thread):
    RE_SEARCH_TOKENS = re.compile(r'\b([^\:]+):("[^"]*"|[^\s]*)')

    def __init__(self, app, filter_keys, text_keys):
        super(AudioIndex, self).__init__()
        self.app = app
        self.filter_keys = filter_keys
        self.text_keys = text_keys
        self.tokenized = defaultdict(lambda:defaultdict(int))
        self.filters = defaultdict(lambda:defaultdict(list))
        self.filters_ci = defaultdict(lambda:defaultdict(list))
        self.metadata = defaultdict(dict)
        self.files = []
        self._ready = False

    def __len__(self):
        return len(self.files)

    def run(self):
        while True:
            start = time.time()

            print "Building audio index"

            for path in self.app.config['AUDIO_PATHS']:
                self.add_path(path)

            print "Done! (%d entries, took %.2fs)" % (len(self), time.time() - start)

            self._ready = True
            
            time.sleep(3)
        
    def add_path(self, path):
        for fn in os.listdir(path): 
            if fn.startswith('.'):
                continue

            full_path = os.path.join(path, fn)

            try:
                unicode(full_path)
            except:
                continue
            
            if os.path.isdir(full_path):
                self.add_path(full_path)
            elif fn.endswith('.mp3'):
                if full_path in self.files:
                    continue

                metadata = EasyID3(full_path)
                audio = MP3(full_path)

                self.metadata[full_path]['length'] = audio.info.length

                tokens = []
                for key in ('artist', 'title', 'album', 'genre'):
                    try:
                        value = unicode(metadata[key][0])
                    except (IndexError, KeyError):
                        continue

                    lower_value = value.lower()

                    self.metadata[full_path][key] = value

                    if key in self.text_keys:
                        tokens.extend(filter(None, lower_value.split(' ')))

                    if key in self.filter_keys:
                        self.filters[key][value].append(full_path)
                        self.filters_ci[key][lower_value].append(full_path)

                self.files.append(full_path)

                for token in tokens:
                    self.tokenized[token][full_path] += 1
                    
    def search(self, query):
        text_results = defaultdict(int)
        filter_results = defaultdict(int)

        tokens = self._get_search_query_tokens(query.lower())
        text_tokens = tokens.pop('', None)

        for token, value in tokens.iteritems():
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            if value in self.filters_ci[token]:
                for full_path in self.filters_ci[token][value]:
                    filter_results[full_path] += 1

        if tokens and not filter_results:
            return None

        if text_tokens:
            for token in text_tokens.split(' '):
                for full_path, count in self.tokenized[token].iteritems():
                    text_results[full_path] += count
        
        if filter_results:
            # We need to remove any results which didnt match filters
            results = {}
            for full_path, count in filter_results.iteritems():
                if not text_tokens or text_results[full_path]:
                    results[full_path] = text_results[full_path] + count
        else:
            results = text_results

        if not results:
            return None

        return sorted(results.items(), key=lambda x: -x[1])[:50]

    def _get_search_query_tokens(self, query):
        """
        Parses a search query for supported tokens and returns a dictionary.

        e.g., "author:test my message" -> {'author': 'test', '': 'my message'}

        """
        tokens = defaultdict(str)
        def _token_repl(matchobj):
            tokens[matchobj.group(1)] = matchobj.group(2)
            return ''
        query = self.RE_SEARCH_TOKENS.sub(_token_repl, query.strip()).strip()
        if query:
            tokens[''] = query
        return tokens

class AudioThread(threading.Thread):
    def __init__(self, app, index):
        self.app = app

        self.current_song = None

        self.queue_pos = 0
        self.playlist = []
        
        self.pos_cur = 0
        self.pos_end = 0
        

        self.index = index

        self._skipped = False
        self._playing = False
        self._ready = False

        super(AudioThread, self).__init__()
        
    def run(self):
        while True:
            time.sleep(0.1)
            
            if not self.index._ready:
                continue
            
            self._ready = True
            
            if not self.playlist:
                continue

            if self.queue_pos >= len(self.playlist):
                self.queue_pos = 0

            self.play_song(self.playlist[self.queue_pos])
        
            self.queue_pos += 1

        self.pyaudio.terminate()

    def play_song(self, filename):
        self._playing = True
        self._skipped = False

        metadata = self.index.metadata[filename]

        # for channel in bot.config.channels:
        #     bot.msg(channel, 'Now playing: %s - %s' % (metadata.get('artist'), metadata.get('title')))

        self.current_song = filename
        self.pos_cur = 0
        self.pos_end = metadata['length']
        
        p = pyaudio.PyAudio()
        
        if filename.endswith('.wav'):
            af = wave.open(filename, 'rb')
            rate = af.getframerate()
            channels = af.getnchannels()
            format = p.get_format_from_width(af.getsampwidth())
            audio = 'wav'
        else:
            af = mad.MadFile(filename)
            rate = af.samplerate()
            channels = 2
            format = p.get_format_from_width(pyaudio.paInt32)
            audio = 'mp3'

        # open stream
        stream = p.open(
            format = format,
            channels = channels,
            rate = rate,
            output = True,
        )

        try:
            while True:
                if self._skipped:
                    break
                
                if not self._playing:
                    time.sleep(0.1)
                    continue

                data = af.read()
                if not data:
                    break

                # Wait until we can continue streaming
                stream.write(data)

                try:
                    self.pos_cur = stream.get_time()
                except IOError:
                    pass
        finally:
            stream.close()
            p.terminate()
    
    def is_playing(self):
        return self._playing and self.current_song

    def is_stopped(self):
        return not self.is_playing()

    def is_ready(self):
        return self._ready
    
    def stop_audio(self):
        self._playing = False

    def start_audio(self):
        self._playing = True

    def skip_song(self):
        self._skipped = True

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
        self.thread = AudioThread(app, self.index)
        self.thread.start()

    def __getattr__(self, attr):
        if attr in self.__dict__:
            if not self.thread.is_ready():
                return

            return self.__dict__[attr]
        else:
            return getattr(self.thread, attr)

    def shuffle_all(self):
        self.thread.playlist = self.index.files
        random.shuffle(self.thread.playlist)

    def get_song_pos(self):
        return (self.thread.pos_cur, self.thread.pos_end)

    def get_current_song(self):
        if not self.is_ready():
            return

        song = self.thread.current_song
        if not song:
            return

        return self.index.metadata[song]

    def play_random(self):
        if not self.is_ready():
            return
        
        name = self.index.files[random.randint(0, len(self.index.files))]

        return self.play_filename(name)

    def stop_playing(self):
        self.thread.stop_audio()

    def start_playing(self):
        if not self.thread.playlist and not self.thread.current_song:
            self.thread.playlist = list(self.index.files)
            random.shuffle(self.thread.playlist)

        self.thread.start_audio()

    def clear_playlist(self):
        self.thread.playlist = []

    def get_playlist_index(self):
        return self.thread.queue_pos

    def has_playlist(self):
        return bool(self.thread.playlist)

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
            
        for num, song in enumerate(self.thread.playlist[start:end]):
            metadata = self.index.metadata[song]
            
            name = '%s - %s' % (metadata.get('artist'), metadata.get('title'))
            if with_playing:
                yield start + num + 1, name, start + num == current_offset
            else:
                yield start + num + 1, name

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

        self.thread.playlist.append(filename)
        self.thread.stopped = False
        self.thread.skipped = False

    def list_by_metadata(self, key, value=None, limit=None):
        data = self.index.filters[key]
        if value:
            data = data[value]

        for item in data:
            if value:
                metadata = self.index.metadata[item]
                yield item, metadata
            else:
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
