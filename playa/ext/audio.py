from __future__ import absolute_import

import mad
import os
import pyaudio
import random
import threading
import time
import wave
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

class AudioThread(threading.Thread):
    def __init__(self, app):
        self.app = app
        self.stopped = True
        self.skipped = False
        self.current_track = None

        self.queue_pos = 0
        self.playlist = []
        
        self.search_index = {}
        self.audio_index = []
        self.metadata_index = {}
        
        self.pos_current = 0
        self.pos_end = 0
        
        self.is_ready = False

        super(AudioThread, self).__init__()
        
    def run(self):
        start = time.time()

        print "Building audio index"

        for path in self.app.config['AUDIO_PATHS']:
            self.index_path(path)

        print "Done! (%d entries, took %.2fs)" % (len(self.search_index), time.time() - start)
        
        self.is_ready = True
        
        while True:
            time.sleep(0.1)
            
            if self.stopped:
                continue

            if self.queue_pos >= len(self.playlist):
                self.queue_pos = 0
            
            if not self.playlist:
                continue

            self.play_song(self.playlist[self.queue_pos])
            
            self.queue_pos += 1

    def play_song(self, filename):
        self.skipped = False
        self.pos_current = 0

        p = pyaudio.PyAudio()
        metadata = self.metadata_index[filename]

        # for channel in bot.config.channels:
        #     bot.msg(channel, 'Now playing: %s - %s' % (metadata.get('artist'), metadata.get('title')))

        self.current_track = filename
        self.pos_end = metadata['length']
        
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
        stream = p.open(format = format,
                        channels = channels,
                        rate = rate,
                        output = True)

        if audio == 'wav':
            chunk = 1024
            while self.is_playing():
                data = af.readframes(chunk)
                if not data:
                    self.skipped = True
                    continue
                stream.write(data)
                self.pos_current = stream.get_time()
        elif audio == 'mp3':
            while self.is_playing():
                data = af.read()
                if not data:
                    self.skipped = True
                    continue
                stream.write(data)
                self.pos_current = stream.get_time()
            
        stream.close()
        p.terminate()
    
    def is_playing(self):
        return not (self.stopped or self.skipped)

    def index_path(self, path):
        for fn in os.listdir(path): 
            if fn.startswith('.'):
                continue
            full_path = os.path.join(path, fn)
            if os.path.isdir(full_path):
                self.index_path(full_path)
            elif fn.endswith('.mp3'):
                metadata = EasyID3(full_path)
                audio = MP3(full_path)

                self.metadata_index[full_path] = {}
                self.metadata_index[full_path]['length'] = audio.info.length

                tokens = []
                for key in ('artist', 'title', 'album'):
                    try:
                        self.metadata_index[full_path][key] = unicode(metadata[key][0])
                        tokens.extend(map(lambda x: x.lower(), filter(None, metadata[key][0].split(' '))))
                    except KeyError, e:
                        continue

                self.audio_index.append(full_path)

                for token in tokens:
                    if token not in self.search_index:
                        self.search_index[token] = {}
                    if full_path not in self.search_index[token]:
                        self.search_index[token][full_path] = 1
                    else:
                        self.search_index[token][full_path] += 1

class AudioPlayer(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None
            self.thread = None

    def init_app(self, app):
        self.app = app
        self.thread = AudioThread(app)
        self.thread.start()
        # self.app.after_request(self.after_request)
        # self.app.before_request(self.before_request)

    def is_ready(self):
        return self.thread.is_ready

    def is_playing(self):
        return self.thread.current_track and not self.thread.stopped
    
    def is_stopped(self):
        return self.thread.stopped

    def shuffle_all(self):
        self.thread.playlist = self.thread.audio_index
        random.shuffle(self.thread.playlist)

    def get_song_pos(self):
        return (self.thread.pos_current, self.thread.pos_end)

    def get_current_track(self):
        if not self.is_ready():
            return

        song = self.thread.current_track
        if not song:
            return

        return self.thread.metadata_index[song]

    def play_random(self):
        if not self.is_ready():
            return
        
        name = self.thread.audio_index[random.randint(0, len(self.thread.audio_index))]

        return self.play_filename(name)

    def play_next(self):
        self.thread.skipped = True
        self.thread.stopped = False

    def stop_playing(self):
        if not self.is_ready():
            return

        self.thread.stopped = True
        self.thread.skipped = False

    def start_playing(self):
        if not self.is_ready():
            return

        self.thread.stopped = False
        self.thread.skipped = False

        if not self.thread.playlist:
            self.thread.playlist = list(self.thread.audio_index)
            random.shuffle(self.thread.playlist)

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
            metadata = self.thread.metadata_index[song]
            
            name = '%s - %s' % (metadata.get('artist'), metadata.get('title'))
            if with_playing:
                yield start + num + 1, name, start + num == current_offset
            else:
                yield start + num + 1, name

    def find_song(self, query):
        if not self.is_ready():
            return

        results = {}
    
        tokens = query.lower().split(' ')
        for token in tokens:
            if token not in self.thread.search_index:
                continue
            for full_path, count in self.thread.search_index[token].iteritems():
                if full_path not in results:
                    results[full_path] = count
                else:
                    results[full_path] += count
        
        if not results:
            return None

        return sorted(results.items(), key=lambda x: -x[1])[:50]
    
    def get_metadata(self, filename):
        return self.thread.metadata_index[filename]
    
    def play_filename(self, filename):
        if not self.is_ready():
            return

        if not os.path.exists(filename):
            raise ValueError

        self.thread.playlist.append(filename)
        self.thread.stopped = False
        self.thread.skipped = False

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
