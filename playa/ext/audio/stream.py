from __future__ import absolute_import

import threading
import time

from playa.lib import vlc

class AudioStream(threading.Thread):
    def __init__(self, app, index):
        self.app = app

        self.current_song = None

        self.queue = []
        self.queue_pos = 0
        
        self.pos_cur = 0
        self.pos_end = 0

        self.index = index

        self._ready = False
        self._playing = False

        self.vlc = vlc.Instance()
        self.player = self.vlc.media_player_new()

        super(AudioStream, self).__init__()
        
    def run(self):
        while True:
            time.sleep(0.1)
            
            if not self.index._ready:
                continue
            
            self._ready = True
            
            if not self._playing:
                continue
            
            if self.is_playing():
                self.pos_cur = self.player.get_time() / 1000
                self.pos_end = self.player.get_length() / 1000
                continue
            
            if not self.queue:
                continue

            if self.current_song:
                self.queue_pos += 1
            
            if self.queue_pos >= len(self.queue):
                self.queue_pos = 0

            self.play_song(self.queue[self.queue_pos])
        
        self.pyaudio.terminate()

    def play_song(self, filename):
        self.current_song = filename
        self._playing = True
        self.media = self.vlc.media_new(unicode(self.current_song))
        self.player.set_media(self.media)
        self.player.play()

    def is_playing(self):
        return self.player.is_playing()

    def is_stopped(self):
        return not self.is_playing()

    def is_ready(self):
        return self._ready

    def seek(self, pos):
        self.player.set_time(int(self.pos_end * float(pos) * 1000))

    def stop_audio(self):
        self.player.pause()
        self._playing = False

    def start_audio(self):
        self.player.play()
        self._playing = True

    def get_volume(self):
        return self.player.audio_get_volume()
    
    def set_volume(self, arg):
        return self.player.audio_set_volume(int(float(arg)*100))

    def skip_song(self):
        self.player.stop()

